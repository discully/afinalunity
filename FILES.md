# Files

## File Types

| Extension | Description               | Number | Interesting Files          | afu_to_png         | afu_to_json        | afu_to_wav         |
| :---      | :---                      | ---:   | :---                       | :---               | :---               | :---               |
| 3DR       |                           |      9 |                            |                    |                    |                    |
| 3DV       |                           |     49 |                            |                    |                    |                    |
| ANM       |                           |      1 | phaser.anm                 |                    |                    |                    |
| AST       | `multiple (see below)`    |      3 |                            |                    |                    |                    |
| &vellip;  | Panel background image    |      2 | astropnl.ast, compupnl.ast | :heavy_check_mark: |                    |                    |
| &vellip;  | List of sector names      |      1 | sector.ast                 |                    | :heavy_check_mark: |                    |
| BIN       | tactics?                  |     17 |                            |                    |                    |                    |
| BST       | `multiple (see below)`    |   3003 |                            |                    |                    |                    |
| &vellip;  | objects                   |   2561 | o_######.bst               |                    | :heavy_check_mark: |                    |
| &vellip;  | phaser info               |     97 | p_######.bst               |                    | :heavy_check_mark: |                    |
| &vellip;  | terminal display text     |     10 | t_######.bst               |                    | :heavy_check_mark: |                    |
| &vellip;  | conversations             |    182 | w{world}c###.bst           |                    | :heavy_check_mark: |                    |
| &vellip;  | conversations index       |      8 | w_{world}con.bst           |                    | :heavy_check_mark: |                    |
| &vellip;  | screens index             |      9 | w_{world}scrn.bst          |                    | :heavy_check_mark: |                    |
| &vellip;  | screen startups           |      9 | w_{world}strt.bst          |                    | :heavy_check_mark: |                    |
| &vellip;  | screen objects            |    126 | w{world}##obj.bst          |                    | :heavy_check_mark: |                    |
| &vellip;  |                           |      1 | worlname.bst               |                    | :heavy_check_mark: |                    |
| DAT       | `multiple (see below)`    |     15 |                            |                    |                    |                    |
| &vellip;  | cursors                   |      2 | cursor.dat, waitcurs.dat   | :heavy_check_mark: |                    |                    |
| &vellip;  | level data                |      5 | level{level}.dat           |                    |                    |                    |
| &vellip;  | advice index              |      6 | w{world}a000.dat           |                    | :heavy_check_mark: |                    |
| &vellip;  | triggers                  |      1 | trigger.dat                |                    | :heavy_check_mark: |                    |
| &vellip;  | astrogation state?        |      1 | ast_stat.dat               |                    |                    |                    |
| DB        | `multiple (see below)`    |      3 |                            |                    |                    |                    |
| &vellip;  | astrogation database      |      2 | [astro.db, astromap.db](ASTRO.md) |             | :heavy_check_mark: |                    |
| &vellip;  | computer database         |      1 | computer.db                | :heavy_check_mark: | :heavy_check_mark: |                    |
| IMG       | image (mostly 3d textures)|    197 |                            | :heavy_check_mark: |                    |                    |
| DMG       | list of .img files        |      7 | enterprs.dmg               |                    |                    |                    |
| ---       |                           |      2 | list, compstat             |                    |                    |                    |
| FON       | font                      |     10 |                            | :heavy_check_mark: |                    |                    |
| FVF       |                           |     27 |                            |                    |                    |                    |
| LBM       |                           |      4 |                            |                    |                    |                    |
| MAP       |                           |      3 | icon.map, movie.map, phaser.map |               |                    |                    |
| MAC       | audio (sound effects)     |    103 |                            |                    |                    | :heavy_check_mark: |
| LST       | list (index of sprites)   |      1 | sprites.lst                |                    | :heavy_check_mark: |                    |
| MRG       | menu graphics             |     11 |                            | :heavy_check_mark: |                    |                    |
| MTL       |                           |     55 |                            |                    |                    |                    |
| MTR       |                           |      9 |                            |                    |                    |                    |
| PAL       | colour palette            |      1 | standard.pal               |                    |                    |                    |
| PC1       |                           |      9 |                            |                    |                    |                    |
| PC2       |                           |      9 |                            |                    |                    |                    |
| PC3       |                           |      9 |                            |                    |                    |                    |
| PC4       |                           |      9 |                            |                    |                    |                    |
| PC5       |                           |      9 |                            |                    |                    |                    |
| PC6       |                           |      9 |                            |                    |                    |                    |
| PIC       |                           |      4 |                            |                    |                    |                    |
| RAC       | audio (ambient)           |     69 |                            |                    |                    | :heavy_check_mark: |
| RM        | background image (room?)  |      5 | bridge.rm, transp.rm, viewscr.rm | :heavy_check_mark: |              |                    |
| SCR       | `multiple (see below)`    |    153 |                            |                    |                    |                    |
| &vellip;  | world screen background   |     73 | sb{world}{screen}.scr      | :heavy_check_mark: |                    |                    |
| &vellip;  | world                     |      6 | sl{world}.scr              |                    | :heavy_check_mark: |                    |
| &vellip;  | world screen polygons     |     74 | st{world}{screen}.scr      |                    | :heavy_check_mark: |                    |
| SPR       | sprite                    |    666 |                            | :heavy_check_mark: | :heavy_check_mark: |                    |
| SPT       | sprite (transporter room) |      9 |                            | :heavy_check_mark: | :heavy_check_mark: |                    |
| TXT       | text (credits)            |      2 |                            |                    |                    |                    |
| VAC       | audio (voice)             |  10182 |                            |                    |                    | :heavy_check_mark: |
| &vellip;  | computer status alerts    |     23 | cm_###.vac                 |                    |                    | :heavy_check_mark: |
| &vellip;  | object descriptions       |   1170 | ##l#{character}##.vac      |                    |                    | :heavy_check_mark: |
| &vellip;  | triggered speech          |     63 | ##t#{character}##.vac      |                    |                    | :heavy_check_mark: |
| &vellip;  | conversation              |   7235 | fe{character}####.vac      |                    |                    | :heavy_check_mark: |
| &vellip;  | conversation              |   1691 | ####{character}##.vac      |                    |                    | :heavy_check_mark: |

### Characters
* 00 - Picard
* 01 - Riker (number one, of course)
* 02 - Data
* 03 - Troi
* 04 - Worf
* 05 - Crusher
* 06 - La Forge
* 07 - Carlstrom
* 08 - Butler
* 09 - Computer
* ff - other characters

### Worlds
* 00 - 
* 02 - Allanor
* 03 - Morassia
* 04 - Mertens Orbital Station
* 05 - Frigis (Shonoisho Epsilon VI)
* 06 -
* 07 -
* 10 - 
* 5f - Enterprise Bridge
