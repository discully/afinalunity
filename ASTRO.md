# Astrogation

The game space consists of an 8x8x8 grid of 512 sectors.
Each sector has a 20x20x20 co-ordinate grid, some of which will contain a star system.
This means everything can be located within a 160x160x160 grid (global co-ordinates).
There are 2860 star systems in total.

## In-Game Space

Information on a subset of locations in the game.
Useful when examining the astrogation files.

### Starbases

There are 2 starbases in total.

| Starbase     | Sector | Planet |
| :---         | :---   | :---   |
| Starbase 131 | 1-3-1  | Hastings Alpha I |
| Starbase 45  | 0-4-5  | Godel Alpha I |


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

There are 9 outposts in total.

| Outpost     | Sector | Planet          |
| :---        | :---   | :---            |
| Outpost 341 | 3-4-1  | Vanuma Alpha II |
| Outpost 146 | 1-4-6  | Zhalu Zeta I    |


### Navigation and Scanning Buoys

There are 14 navigational and scanning buoys in total.


### Comm Relay

There are 34 comm relays in total.


### Places of Interest

| Name | Sector | System | Co-ordinates | Notes |
| :---   | :---         | :---   | :---         | :---  |
| Al'din | 5-6-3        |        |              | Location from which the Gombara Pulsar can be viewed |
| Thang  | 3-1-3        |        | 9-14-16      | Location of the Unity device |


## File Formats

There are two files covering astrogation: astro.db and astromap.db.

String offsets will either be null (0xFFFFFFFF) or, in astro.db, may be an offset from 0x3e3e0.

### astro.db

|  Offset | Offset | Name              | Type                       | Description |
|  ---:   | ---:   | :---              | ---:                       | :---        |
|    0x00 |        | sectors           | SECTOR[4096]               |  |
| 0x18000 |  98304 | systems           | SYSTEM[]                   |  |
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
|   0x14 |     20 | \<unknown>           |  32u[4] |  |

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
 * Whether the system has been scanned
 * Number of planets it contains

| Offset | Offset | Name                 | Type | Description |
| ---:   | ---:   | :---                 | ---: | :---        |
|   0x00 |      0 | system_index         |  32u |  |
|   0x04 |      4 | system_id            |  16u |  |
|   0x06 |      6 | system_type          |  16u | See Object Types below. Always 32 (0x20). |
|   0x08 |      8 | \<unknown 0>         |   8u | Most are 255 or 0. Five special systems have other values. Possibly cut-scenes or other actions on arrival? |
|   0x09 |      9 | \<unknown 1>         |   8u | Lots of different values |
|   0x0A |     10 |                      |  16u | Always zero |
|   0x0C |     12 | system_x             |  32u | Global co-ordinate x |
|   0x10 |     16 | system_y             |  32u | Global co-ordinate y |
|   0x14 |     20 | system_z             |  32u | Global co-ordinate z |
|   0x18 |     24 |                      |  32u | Always zero |
|   0x1C |     28 | system_name          |  32u | String offset |
|   0x20 |     32 | system_flags         |  16u | Bitfield, see "System Flags" below |
|   0x22 |     34 | system_station_orbit |   8u | 0 or, in astromap.db if a station is present, the index of the planet after which the station orbits |
|   0x23 |     35 | system_station_type  |   8u | 0 or, in astromap.db is a station is present, either 131 (station) or 132 (outpost) |
|   0x24 |     36 | system_class         |  16u | See "System Class" below. |
|   0x26 |     38 | system_magnitude     |  16s | Divide by 10.0 to get the magnitude of the primary star |
|   0x28 |     40 | \<unknown 2>         |  32u | Values between 0 and 255 |
|   0x2C |     44 |                      |  32u | Always zero |
|   0x30 |     48 | system_alias         |  32u | String offset to an alternative name (e.g. "Frigis" for _______) |
|   0x34 |     52 | system_notable       |  32u | String offset to the name of a notable planet within the system |
|   0x38 |     56 | system_description   |  32u | String offset to description of the system |
|   0x3C |     60 |                      |  32u | Always zero |
|   0x40 |     64 | system_station       |  32u | Only in astromap.db for systems with stations. Separation is 36bytes == sizeof(station). Offset? But what file? |

Total length: 70 bytes.

#### System Flags

The system_flags field is a bitfield encoding the following values:
 * 0b1 - Primary star is a White Dwarf
 * 0b10 - A binary star system
 * 0b1100 - Contains a starbase
 * 0b0100 - Contains an outpost
 * 0b10000 - Contains an inhabited planet


#### System Class

The system_class field defines the class of the system's primary star.

The first part of the star's class comes from the result of integer
division by 10, which is an index into this array: \['O', 'B', 'A', 'F', 'G', 'K', 'M'].

The second part of the star's class comes from th remainder
when divided by 10.

For example, 34 would mean the system contains a class "F4" star.


### Struct: STATION

| Offset | Offset | Name                 | Type | Description |
| ---:   | ---:   | :---                 | ---: | :---        |
|   0x00 |      0 |                      |  32u | Always zero |
|   0x04 |      4 | station_id           |  16u |             |
|   0x06 |      6 | station_type         |  16u | See Object Types below |
|   0x08 |      8 |                      |  32u | Always zero |
|   0x0C |     12 | station_x            |  32u | Global co-ordinate x |
|   0x10 |     16 | station_y            |  32u | Global co-ordinate y |
|   0x14 |     20 | station_z            |  32u | Global co-ordinate z |
|   0x18 |     24 |                      |  32u | Always zero |
|   0x1C |     28 | station_name         |  32u | String offset of name of station |
|   0x20 |     32 | station_sector_id    |  16u | ID of sector station resides in  |
|   0x22 |     34 | station_sector_index |   8u | Index of system station resides in |
|   0x23 |     35 | station_orbit_index  |   8u | Index of planet after which station orbits (e.g. if index is 2, station orbits between the 3rd and 4th planets)

Total Length: 36 bytes.


### Struct: BODY

Represents astronomical bodies: Ion Storms, Quasaroids, Black Holes, Subspace Vortecies, and other special objects (Alien device, Unity device, Ruinore sector, Ayers, Singelea sector).

| Offset | Offset | Name         | Type | Description |
| ---:   | ---:   | :---         | ---: | :---        |
|   0x00 |    0 | body_index       | 32u  |  |
|   0x04 |    4 | body_id          | 16u  |  |
|   0x06 |    6 | body_type        | 16u  | See Object Types below |
|   0x08 |    8 |                  | 32u  | Always zero |
|   0x0C |   12 | body_x           | 32u  | Global co-ordinate x |
|   0x10 |   16 | body_y           | 32u  | Global co-ordinate y |
|   0x14 |   20 | body_z           | 32u  | Global co-ordinate z |
|   0x18 |   24 |                  | 32u  | Always zero |
|   0x1C |   28 | body_name        | 32u  | String offset of name of body |
|   0x22 |   32 | body_zone_radius | 32u  | Radius of known zone of influence, in LY |
|   0x26 |   36 | \<unknown>       | 32u  | 0 in astro.db, non-zero in astromap.db |

Total length: 40 bytes.

### Object types
 * 32: "Star System"
 * 65: "Ion Storm"
 * 66: "Quasaroid"
 * 68: "Black Hole"
 * 69: "Subspace Vortex"
 * 72: "Unity Device" - In astromap.db (in astro.db this is 73)
 * 73: "Special item"
   * Alien device - the one which attacks Mertens Orbital Station
   * Unity device
   * Ruinore sector
   * Ayers
   * Singelea sector
 * 128: "Deep Space Station"
 * 129: "Comm Relay"
 * 130: "Buoy"
 * 131: "Starbase"
 * 132: "Outpost"
