from argparse import ArgumentParser
from base64 import b64encode 
from io import BytesIO
from pathlib import Path
from struct import pack
import pygltflib
import AFU


# UVs are stored as 16.16 fixed point (65536 == 1.0).
UV_SCALE = 65536.0


class BufferBuilder:
	"""Packs binary data into a single glTF buffer, adding bufferViews and accessors."""

	def __init__(self, gltf):
		self.gltf = gltf
		self.blob = bytearray()

	def add(self, data, component_type, accessor_type, count, target, bounds=None):
		while len(self.blob) % 4:  # glTF requires 4-byte aligned views
			self.blob.append(0)
		self.gltf.bufferViews.append(pygltflib.BufferView(
			buffer=0, byteOffset=len(self.blob), byteLength=len(data), target=target))
		self.blob += data

		accessor = pygltflib.Accessor(
			bufferView=len(self.gltf.bufferViews) - 1,
			componentType=component_type, count=count, type=accessor_type)
		if bounds:
			accessor.min, accessor.max = bounds
		self.gltf.accessors.append(accessor)
		return len(self.gltf.accessors) - 1


def _pack_floats(vectors):
	flat = [c for v in vectors for c in v]
	return pack(f"<{len(flat)}f", *flat)


def _png_data_uri(image):
	"""Encode a PIL image as a PNG data URI. Returns (uri, has_transparency)."""
	has_alpha = "A" in image.getbands() or "transparency" in image.info
	if image.mode not in ("RGB", "RGBA"):
		image = image.convert("RGBA" if has_alpha else "RGB")
	transparent = image.mode == "RGBA" and image.getchannel("A").getextrema()[0] < 255

	buffer = BytesIO()
	image.save(buffer, format="PNG")
	uri = "data:image/png;base64," + b64encode(buffer.getvalue()).decode("ascii")
	return uri, transparent


# The game uses +Y down and +Z forward (the saucer is at +Z, the hull bottom has
# the larger Y). Rotating 180 degrees about Z gives glTF's +Y up / +Z front and,
# being a pure rotation, keeps the triangle winding and normals valid.
def _transform(v):
	return (-v[0], -v[1], v[2])


def _convert(model, material, textures):
	"""Build a pygltflib.GLTF2 from the parsed model, material and textures."""
	gltf = pygltflib.GLTF2(asset=pygltflib.Asset(version="2.0", generator="afu_to_gltf"))
	gltf.scene = 0
	gltf.scenes = [pygltflib.Scene(nodes=[])]
	builder = BufferBuilder(gltf)
	entries = material["entries"]

	# UVs run 0..1 inclusive, so clamp to avoid bleeding across the edge.
	gltf.samplers.append(pygltflib.Sampler(
		magFilter=pygltflib.LINEAR, minFilter=pygltflib.LINEAR,
		wrapS=pygltflib.CLAMP_TO_EDGE, wrapT=pygltflib.CLAMP_TO_EDGE
		))

	for index, entry in enumerate(entries):
		image = textures[index]
		name = Path(entry["img_file"]).stem if image is not None else f"untextured_{index}"
		pbr = pygltflib.PbrMetallicRoughness(metallicFactor=0.0, roughnessFactor=1.0)
		gltf_material = pygltflib.Material(
			name=name, pbrMetallicRoughness=pbr, extras={"mtl_type": entry["type"]})

		if image is None:
			pbr.baseColorFactor = [0.6, 0.6, 0.6, 1.0]
		else:
			uri, transparent = _png_data_uri(image)
			gltf.images.append(pygltflib.Image(uri=uri, name=name))
			gltf.textures.append(pygltflib.Texture(source=len(gltf.images) - 1, sampler=0))
			pbr.baseColorTexture = pygltflib.TextureInfo(index=len(gltf.textures) - 1)
			if transparent:
				gltf_material.alphaMode = "MASK"

		gltf.materials.append(gltf_material)

	for mesh_index, mesh in enumerate(model["meshes"]):
		if not mesh["faces"]:
			continue

		positions = [_transform(v) for v in mesh["vertices"]]
		normals = [_transform(n) for n in mesh["vertices_normals"]]
		bounds = (
			[min(p[k] for p in positions) for k in range(3)],
			[max(p[k] for p in positions) for k in range(3)]
			)

		attributes = pygltflib.Attributes(
			POSITION=builder.add(
				_pack_floats(positions), pygltflib.FLOAT, pygltflib.VEC3,
				len(positions), pygltflib.ARRAY_BUFFER, bounds),
			NORMAL=builder.add(
				_pack_floats(normals), pygltflib.FLOAT, pygltflib.VEC3,
				len(normals), pygltflib.ARRAY_BUFFER)
			)

		if "uvs" in mesh:
			uvs = [(u / UV_SCALE, v / UV_SCALE) for u, v in mesh["uvs"]]
			attributes.TEXCOORD_0 = builder.add(
				_pack_floats(uvs), pygltflib.FLOAT, pygltflib.VEC2,
				len(uvs), pygltflib.ARRAY_BUFFER)

		# One primitive per material; they all share the mesh's vertex accessors.
		indices_by_material = {}
		for face in mesh["faces"]:
			indices_by_material.setdefault(face["material"], []).extend(face["vertices"])

		wide = len(positions) > 0xFFFF
		primitives = []
		for material_index, indices in indices_by_material.items():
			accessor = builder.add(
				pack(f"<{len(indices)}{'I' if wide else 'H'}", *indices),
				pygltflib.UNSIGNED_INT if wide else pygltflib.UNSIGNED_SHORT,
				pygltflib.SCALAR, len(indices), pygltflib.ELEMENT_ARRAY_BUFFER
				)
			primitives.append(pygltflib.Primitive(
				attributes=attributes, indices=accessor,
				material=material_index, mode=pygltflib.TRIANGLES))

		gltf.meshes.append(pygltflib.Mesh(name=f"mesh_{mesh_index}", primitives=primitives))
		gltf.nodes.append(pygltflib.Node(
			name=f"mesh_{mesh_index}", mesh=len(gltf.meshes) - 1,
			extras={"vertices_flag": mesh["vertices_flag"]}
			))
		gltf.scenes[0].nodes.append(len(gltf.nodes) - 1)

	gltf.buffers = [pygltflib.Buffer(byteLength=len(builder.blob))]
	gltf.set_binary_blob(bytes(builder.blob))
	gltf.convert_buffers(pygltflib.BufferFormat.DATAURI)

	return gltf


def main():	
	parser = ArgumentParser(description="Convert .3dv, .3dr, and .pc* 3d models to glTF")
	parser.add_argument("model_file", help="Path to the .3dv, .3dr or .pc* 3D model file", type=Path)
	parser.add_argument("-o", "--output_dir", type=Path, help="Output directory to place glTF in", default=".")
	parser.add_argument("-d", "--damaged", action="store_true", help="Use damaged model textures")
	args = parser.parse_args()

	file_type = AFU.identify(args.model_file)

	if not file_type == AFU.FileType.G3D_OBJECT:
		print(f"Unsupported file type: {file_type}")
		return

	model = AFU.Graphics.model(args.model_file)

	material_suffix = ".mtr" if args.model_file.suffix.lower() == ".3dr" else ".mtl"
	if args.damaged and material_suffix == ".mtl":
		material_suffix = ".dmg"
	material = AFU.Graphics.material(args.model_file.with_suffix(material_suffix))

	textures = []
	for entry in material["entries"]:

		if entry["img_file"] == "":
			textures.append(None)
			continue

		texture_file = args.model_file.with_name(entry["img_file"])
		if texture_file.suffix.lower() == ".img":
			textures.append(AFU.Graphics.img(texture_file)["image"].pilImage().image)
		elif texture_file.suffix.lower() == ".lbm":
			textures.append(AFU.Graphics.lbm(texture_file)["image"].pilImage().image)
		else:
			textures.append(None)

	gltf = _convert(model, material, textures)

	if args.damaged:
		output_file_path = args.output_dir.joinpath("d" + args.model_file.name + ".gltf")
	else:
		output_file_path = args.output_dir.joinpath(args.model_file.name + ".gltf")
	gltf.save(output_file_path)


if __name__ == "__main__":
	main()