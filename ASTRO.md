# Astrogation

The game space is known as the 'Kridnar navigation block' and consists of an 8x8x8 grid of 512 sectors.
Each sector has a 20x20x20 co-ordinate grid, some of which will contain a star system.
This means everything can be located within a 160x160x160 grid (global co-ordinates).
There are 2860 star systems in total.

| Alignment       | Sectors | Systems |
| :---            | ---:    | ---:    |
| Z'Tarnis Nebula |     143 |     800 |
| Non-aligned     |      78 |     423 |
| Federation      |     128 |     727 |
| Neutral Zone    |      48 |     258 |
| Romulan         |     115 |     652 |


## In-Game Space

Information on a subset of locations in the game.
Useful when examining the astrogation files.

### Starbases

There are 2 starbases in total.

| Starbase     | Sector | System  | Planet           |
| :---         | :---   | :---    | :---             |
| Starbase 131 | 1-3-1  | 18-3-5  | Hastings Alpha I |
| Starbase 45  | 0-4-5  | 3-10-10 | Godel Alpha I    |


### DS Stations

There are 5 deep space stations in total.

| Station                | Sector | Coordinates |
| :---                   | :---   | :---        |
| Deep Space Station 220 | 2-2-0  | 9-16-17     |
| Deep Space Station 633 | 6-3-3  | 10-9-12     |
| Deep Space Station 175 | 1-7-5  | 12-7-14     |
| Deep Space Station 6   | 0-0-6  | 6-10-9      |
| Deep Space Station 161 | 1-6-1  | 10-8-17     |


### Outposts

There are 9 outposts in total. 8 regular outposts, and Outpost Delta-0-8.

| Outpost           | Sector | System   | Planet                 |
| :---              | :---   | :---     | :---                   |
| Outpost 146       | 1-4-6  | 14-16-5  | Zhalu Zeta I           |
| Outpost 172       | 1-7-2  | 12-6-16  | Myborn Beta II         |
| Outpost 174       | 1-7-4  | 6-10-14  | Vavuru Delta II        |
| Outpost 341       | 3-4-1  | 18-10-16 | Vanuma Alpha II        |
| Outpost 430       | 4-3-0  | 14-7-11  | Optima Alpha II        |
| Outpost 435       | 4-3-5  | 5-1-4    | Rydle Eta II           |
| Outpost 543       | 5-4-3  | 0-5-1    | Goldur Eta II          |
| Outpost 644       | 6-4-4  | 2-12-16  | Bonar Epsilon I        |
| Outpost Delta-0-8 | 6-3-4  | 11-14-6  | Kamyar Delta (Yajj) IV |


### Navigation and Scanning Buoys

There are 14 navigational and scanning buoys in total.


### Comm Relay

There are 34 comm relays in total.


### Places of Interest

| Name      | Sector          | System  | Co-ordinates | Notes |
| :---      | :---            | :---    | :---      | :---  |
|           | M'kyru    4-4-4 |         | | Where you start the game and meet the Garidian warbird |
|           | Ruinore   3-4-3 |         | | Where you are supposed to be patrolling the neutral zone |
| Palmyra   | M'kyru    4-4-4 | Zeta    | | If you don't chalenge the Garidian warbird, the scout ship self destructs, and you detect escape pods here |
| Cymkoe    | Steger    4-3-2 | Delta   | 92-76-56  | Mission 1 - Contains "Cymkoe IV", location of Mertens Orbital Station |
| Morassia  | Euterpe   2-2-5 | Epsilon | 55-50-101 | Mission 2 - The zoo planet, where Dr Hyunh-Foertsch goes missing. |
| Joward    | Cashat    1-3-6 | Delta   | | Go to Joward III in search of Ferengi trader. Upon arrival, crew advises going to Nigold System. |
| Nigold    | Teagra    2-3-6 | Epsilon | | Location of Ferengi trader, Aramut |
| Frigis    | Shonoisho 4-2-5 | Epsilon | 88-45-105 | Mission 3 - The Garidian colony on Shonoisho Epsilon VI (aka Frigis) |
|           | Goldur    5-4-3 | Eta     | | Location of Outpost 543, and Commander Chan (dialogue says Goldur Delta, but it's in Eta) |
| Paxanona  | Goldur    5-4-3 |         | 11-90-65  | Location of Comm Relay 543, which you defend from the Romulans |
| Beremar   | Goldur    5-4-3 | Delta   | | USS Ayers (Ambassador class, commanded by Capt. Ward) which you're sent to join... but too late |
| Balis     | Goldur    5-4-3 | Epsilon | | Location of IKS Bortas, commanded by Captain Ky'Dra |
| Horst     | Tothe     5-4-4 | Delta   | 106-84-99 | Mission 4 - Contains "Horst III". You first visit the vulcan archeologist Shanok here, then again for the mission. |
| Yajj      | Kamyar    6-3-4 | Delta   | 131-74-86 | Location of Outpost Delta-0-8, at Yajj IV, which you're ordered to go defend |
| Allanor   | Brinus    2-6-2 | Zeta    | | Mission 5 - Location of the Chodak ruins |
|           | Al'din    5-6-7 |         |              | Location from which the Gombara Pulsar can be viewed |
|           | Thang     3-1-3 |         | 69-34-76     | Location of the Unity device |



## File Formats

There are two files covering astrogation: astro.db and astromap.db.

String offsets will either be null (0xFFFFFFFF) or, in astro.db, may be an offset from 0x3e3e0.

### astro.db
todo: some of these offsets are wrong!
|  Offset | Offset | Name              | Type                       | Description |
|  ---:   | ---:   | :---              | ---:                       | :---        |
|    0x00 |        | sectors           | SECTOR[512]                |  |
|  0x4800 |  18432 | systems           | SYSTEM[2860]               |  |
| 0x33fb0 |        | bodies            | BODY[]                     |  |
| 0x3dad8 |        | n_stations_sector | 32u                        |  |
| 0x3dadc |        | n_stations_system | 32u                        |  |
| 0x3dae0 |        | stations          | STATION[n_stations_sector] |  |
|         |        | stations          | STATION[n_stations_system] |  |
| 0x3e3e0 |        | strings           | string[]                   |  |

### astromap.db

|  Offset | Offset | Name           | Type        | Description |
|  ---:   | ---:   | :---           | ---:        | :---        |
|    0x00 |      0 | sector_offsets | 32u[512]    | Offsets into the file of all the sector structs |
|  0x4000 |  16384 | sectors        | sectors[512] | 512 sector data, arranged as per table below |

At each of the sector_offsets, you will find the following data for a given sector:

|  Offset | Offset | Name     | Type      | Description |
|  ---:   | ---:   | :---     | ---:      | :---        |
|    0x00 |      0 | sector   | SECTOR    | Information on the sector |
|    0x24 |     36 | systems  | SYSTEM[]  | Array of the systems within the sector |
|         |        | bodies   | BODY[]    | Array of the astronomical bodies within the sector |
|         |        | stations | STATION[] | Array of the stations within the sector |

### Struct: SECTOR

| Offset | Offset | Name                 | Type | Description |
| ---:   | ---:   | :---                 | ---: | :---        |
|   0x00 |      0 | sector_id            |  32u |  |
|   0x04 |      4 | sector_n_systems     |  32u | Number of systems within sector |
|   0x08 |      8 | sector_n_bodies      |  32u | Number of astronomical bodies within sector |
|   0x0C |     12 | sector_n_stations    |  32u | 0 or, in stromap.db, number of stations within sector |
|   0x10 |     16 | sector_alignment     |  32u | See "Sector Alignment" below |
|   0x14 |     20 | sector_ptr_systems   |  32u | Set during execution. Points to the sector's systems |
|   0x18 |     24 | sector_ptr_bodies    |  32u | Set during execution. Points to the sector's bodies |
|   0x1b |     28 | sector_ptr_stations  |  32u | Set during execution. Points to the sector's stations |
|   0x1f |     32 | sector_ptr_desc      |  32u | Set during execution. Point to the sector description |

Total length: 36 bytes.

#### Sector Alignment
 * 0: Federation
 * 1: Romulan
 * 2: Neutral zone
 * 3: Z'Tarnis Nebula
 * 4 Non-aligned


### Struct: SYSTEM

I have not identified where the following information is stored:
 * Presence of an asteroid belt
 * Number or type of planets/moons it contains

| Offset | Offset | Name                 | Type | Description |
| ---:   | ---:   | :---                 | ---: | :---        |
|   0x00 |      0 | system_index         |  32u | System's index within its sector |
|   0x04 |      4 | system_id            |  16u |  |
|   0x06 |      6 | system_type          |  16u | See Object Types below. Always 32 (0x20). |
|   0x08 |      8 | system_random_seed   |  32u | Used during execution to seed generation of planets, etc.  |
|   0x0C |     12 | system_x             |  32u | Global co-ordinate x |
|   0x10 |     16 | system_y             |  32u | Global co-ordinate y |
|   0x14 |     20 | system_z             |  32u | Global co-ordinate z |
|   0x18 |     24 | system_ptr_desc      |  32u | Set during execution. Points to the system's description |
|   0x1C |     28 | system_name_offset   |  32u | String offset to system's name |
|   0x20 |     32 | system_flags         |  16u | Bitfield, see "System Flags" below |
|   0x22 |     34 | system_station_orbit |   8u | 0 or, if a station is present, the index of the planet which the station orbits |
|   0x23 |     35 | system_station_type  |   8u | 0 or, if a station is present, either 131 (station) or 132 (outpost) |
|   0x24 |     36 | system_star_class    |  16u | See "System Star Class" below. |
|   0x26 |     38 | system_magnitude     |  16s | Divide by 10.0 to get the magnitude of the primary star |
|   0x28 |     40 | \<unknown 2>         |  32u | Used during execution to generate planets, etc. |
|   0x2C |     44 | system_n_planets     |  32u | Set during execution |
|   0x30 |     48 | system_alias_offset  |  32u | String offset to an alternative name (e.g. "Frigis") |
|   0x34 |     52 | system_notable_name  |  32u | String offset to the name of a notable planet within the system |
|   0x38 |     56 | system_notable_desc  |  32u | String offset to description of a notable planet within the system |
|   0x3C |     60 | system_ptr_planets   |  32u | Set during execution. Points to the system's planets |
|   0x40 |     64 | system_ptr_station   |  32u | Set during execution. Points to the system's stations |

Total length: 68 bytes.

#### System Flags

The system_flags field is a bitfield encoding the following values:
 * 0x1 - Primary star is a White Dwarf
 * 0x2 - A binary star system
 * 0x4 - Contains a station (starbase or outpost)
 * 0x8 - Station is an outpost
 * 0x10 - Contains an inhabited planet (astro.db). Unknown property (astromap.db)


#### System Star Class

The system_class field defines the class of the system's primary star.

The first part of the star's class comes from the result of integer
division by 10, which is an index into this array: \['O', 'B', 'A', 'F', 'G', 'K', 'M'].

The second part of the star's class comes from the remainder
when divided by 10.

For example, 34 would mean the system contains a class "F4" star.


### Struct: STATION

| Offset | Offset | Name                 | Type | Description |
| ---:   | ---:   | :---                 | ---: | :---        |
|   0x00 |      0 | station_index        |  32u | not used? |
|   0x04 |      4 | station_id           |  16u |             |
|   0x06 |      6 | station_type         |  16u | See Object Types below |
|   0x08 |      8 | station_random_seed  |  32u | not used? |
|   0x0C |     12 | station_x            |  32u | Global co-ordinate x |
|   0x10 |     16 | station_y            |  32u | Global co-ordinate y |
|   0x14 |     20 | station_z            |  32u | Global co-ordinate z |
|   0x18 |     24 | station_ptr_desc     |  32u | Set during execution. Points to the station's description |
|   0x1C |     28 | station_name_offset  |  32u | String offset of name of station |
|   0x20 |     32 | station_sector_id    |  16u | ID of sector station resides in  |
|   0x22 |     34 | station_system_index |   8u | Index of system station resides in |
|   0x23 |     35 | station_orbit        |   8u | Index of planet which station orbits |

Total Length: 36 bytes.


### Struct: BODY

Represents astronomical bodies: Ion Storms, Quasaroids, Black Holes, Subspace Vortecies, and other special objects (Alien device, Unity device, Ruinore sector, Ayers, Singelea sector).

| Offset | Offset | Name         | Type | Description |
| ---:   | ---:   | :---         | ---: | :---        |
|   0x00 |    0 | body_index       | 32u  | Body's index within its sector |
|   0x04 |    4 | body_id          | 16u  |  |
|   0x06 |    6 | body_type        | 16u  | See Object Types below |
|   0x08 |    8 | body_random_seed | 32u  | not used? |
|   0x0C |   12 | body_x           | 32u  | Global co-ordinate x |
|   0x10 |   16 | body_y           | 32u  | Global co-ordinate y |
|   0x14 |   20 | body_z           | 32u  | Global co-ordinate z |
|   0x18 |   24 | body_ptr_desc    | 32u  | Set during execution. Points to the body's description |
|   0x1C |   28 | body_name_offset | 32u  | String offset of name of body |
|   0x22 |   32 | body_zone_radius | 32u  | Radius of known zone of influence, in LY |
|   0x26 |   36 | \<unknown>       | 32u  | 0 in astro.db, non-zero in astromap.db |

Total length: 40 bytes.

### Object types
 * 32: "Star System"
 * 33: "Planet"
 * 34: "Moon"
 * 64: *"Antimatter Cloud"* :question:
 * 65: "Ion Storm"
 * 66: "Quasaroid"
 * 67: *"Rogue Planet"* :question:
 * 68: "Black Hole"
 * 69: "Subspace Vortex"
 * 72: "Unity Device" - In astromap.db (in astro.db the Unity Device is 73)
 * 73: "Special item"
   * Alien device - the one which attacks Mertens Orbital Station
   * Unity device
   * Ruinore sector
   * USS Ayers
   * Singelea sector
 * 128: "Deep Space Station"
 * 129: "Comm Relay"
 * 130: "Buoy"
 * 131: "Starbase"
 * 132: "Outpost"

 :question: *The Antimatter Cloud and Rogue Planet are present in the executable, but don't appear to be used. Perhaps something not-implemented or removed during development?*
