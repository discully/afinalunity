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
| &vellip;  | terminal display text     |     10 | t_######.bst               |                    |                    |                    |
| &vellip;  | conversations             |    182 | w{world}c###.bst           |                    | :heavy_check_mark: |                    |
| &vellip;  |                           |      8 | w_###con.bst               |                    |                    |                    |
| &vellip;  |                           |      9 | w_##strt.bst               |                    |                    |                    |
| &vellip;  |                           |      9 | w_##scrn.bst               |                    |                    |                    |
| &vellip;  |                           |      9 | w_##scrn.bst               |                    |                    |                    |
| &vellip;  |                           |    126 | w####obj.bst               |                    |                    |                    |
| &vellip;  |                           |      1 | worlname.bst               |                    |                    |                    |
| DAT       | `multiple (see below)`    |     15 |                            |                    |                    |                    |
| &vellip;  | cursors                   |      2 | cursor.dat, waitcurs.dat   |                    |                    |                    |
| &vellip;  | level data                |      5 | level{level}.dat           |                    |                    |                    |
| &vellip;  | world data                |      6 | w{world}a000.dat           |                    |                    |                    |
| &vellip;  | others                    |      2 | ast_stat.dat, trigger.dat  |                    |                    |                    |
| DB        | `multiple (see below)`    |      3 |                            |                    |                    |                    |
| &vellip;  | astrogation database      |      2 | [astro.db, astromap.db](ASTRO.md) |                    | :heavy_check_mark: |                    |
| &vellip;  | computer database         |      1 | computer.db                | :heavy_check_mark: | :heavy_check_mark: |                    |
| IMG       | image (mostly 3d textures)|    197 |                            | :heavy_check_mark: |                    |                    |
| DMG       |                           |      7 |                            |                    |                    |                    |
| ---       |                           |      2 | list, compstat             |                    |                    |                    |
| FON       | font                      |     10 |                            | :heavy_check_mark: |                    |                    |
| FVF       |                           |     27 |                            |                    |                    |                    |
| LBM       |                           |      4 |                            |                    |                    |                    |
| MAP       |                           |      3 | icon.map, movie.map, phaser.map |                    |                    |                    |
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
| RAC       | audio                     |     69 |                            |                    |                    | :heavy_check_mark: |
| RM        | background image (room?)  |      5 | bridge.rm, transp.rm, viewscr.rm | :heavy_check_mark: |                    |                    |
| SCR       |                           |    153 |                            |                    |                    |                    |
| &vellip;  | world screen background   |     73 | sb{world}{screen}.scr      | :heavy_check_mark: |                    |                    |
| &vellip;  | world                     |      6 | sl{world}.scr              |                    | :heavy_check_mark: |                    |
| &vellip;  | world screen polygons     |     74 | st{world}{screen}.scr      |                    | :heavy_check_mark: |                    |
| SPR       | sprite                    |    666 |                            | :heavy_check_mark: | :heavy_check_mark: |                    |
| SPT       | sprite (transporter room) |      9 |                            | :heavy_check_mark: | :heavy_check_mark: |                    |
| TXT       | text (credits)            |      2 |                            |                    |                    |                    |
| VAC       | audio (voice)             |  10182 |                            |                    |                    | :heavy_check_mark: |
| &vellip;  |                           |   7235 | fe{character}####.vac      |                    |                    | :heavy_check_mark: |

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
* ff -

### Worlds
* 002 -
* 003 - Morassia
* 004 - Mertens Orbital Station
* 005 - Frigis (Shonoisho Epsilon VI)
* 006 -
* 007 -
* 05f - Enterprise Bridge
