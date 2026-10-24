# China Set: Trains README

READ IN ENGLISH | [CHINESE](./README-zh.md)

1. General Information
2. Building
3. Credits
4. License
5. 1.15x Scale Fork (GETS compatibility)

## 1. General Information

China Set: Trains is the train sector of the China set of OpenTTD.
China Set: Trains is licensed under GPL v2.

Everything in this set is Mainland China rolling stock, in addition of
several wagon types from international/interregional connections.

Locomotives and multiple units featuring refitting are for liveries.

The default setting should be build year livery, which means that
locomotive, multiple unit or coach will remain on the livery scheme as
built. Another option is to manually choose a livery from liveries
already introduced.

Wagon refitting behaves as in normal OpenTTD, there is cargo-specific
graphics on major part of wagons.

List of available parameters:

| Name                                                    | Function                                                                                                                                         | Default value |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ | ------------- |
| Loading speed                                           | Change wagon loading speed                                                                                                                       | Normal        |
| Purchase cost                                           | Change purchase cost                                                                                                                             | 25%           |
| Running cost                                            | Change running cost                                                                                                                              | 25%           |
| Cargo age period                                        | Change the rate cargo gets aged                                                                                                                  | Standard      |
| Cargo age period for freight wagons                     | Change the rate cargo in mail and freight wagons gets aged; independent from the parameter above                                                | Standard      |
| 25-Series coaches built after 2014 default to be green | Change whether the Type 25 Series Coaches purchased after 2014 default to be olive green. In reality, before 2014, they had different colours. | Yes           |

## 2. Building

The source is available on [GitHub](https://github.com/OpenTTD-China-Set/China-Set-Trains). These tools are required to build the GRF:

- nml
- make
- gcc
- gorender, or renderobject

You would need to render all models first, then you can build the GRF.

> [!NOTE]
> The first build will be slow since all models have to be rendered, which is a slow process.
> You can use `make -j n` to speed up the process by running multiple tasks at once where `n` is the task limit.

Using Linux or WSL:

```bash
#!/bin/bash
# you'll have to install gorender from https://github.com/mattkimber/gorender
# here we use apt for demo

# dependencies
sudo apt install python3
sudo apt install python3-pip
sudo apt install make
pip3 install nml
# we would also need gcc, but that should be already included in most distros

# compiling
make
# alternatively, you could use "make -j n" where n is the total number of parallel tasks you want to run at once.
```

Using Windows (Scoop is advised here, but non-scoop compilations are also possible):

```powershell
# we suggest you to use scoop; you can get scoop @ https://scoop.sh

# dependencies
scoop bucket add main
scoop bucket add openttd https://github.com/WenSimEHRP/OpenTTD-Bucket
scoop install python
scoop install make
scoop install openttd/nml
scoop install openttd/gorender
# we would need the gcc compiler in from mingw
scoop install mingw

# compiling
make
# alternatively, you could use "make -j n" where n is the total number of parallel tasks you want to run at once.
```

## 3. Credits

Contributors (in alphabetical order):

- Ahyangyi
- asAn0
- babel
- ctx (Qipaoxian)
- DF43110
- EMB190
- FJZer0ich
- guangming
- Haiyan
- huanfeng
- jackgqj
- John Franklin
- Mikhail
- NACHN
- nengyeqing
- shentie106
- SL-1230
- WenSim
- wuwu (kaitokiwa)

If you want to know the author of the specific vox, click [here](docs/contributor.csv).

Thanks to:

- andythenorth
- Belaja Lilija
- dP
- Emperor Jake
- Garlic_Bread42
- KeepinItRail
- peter1138
- planetmaker
- Simo333
- Timberwolf
- 2cc Trainset Team
- Finnish Trainset Team
- JP+ Team
- xUSSR Team

Special thanks to everyone whom thanks is due;
Patch Pack Developers, especially JGR;
OpenTTD Developers; and Chris Sawyer.

## 4. License

```text
China Set: Trains

Copyright (C) 2023-2025 China Set Team

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, please check
https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html
```

## 5. 1.15x Scale Fork (GETS compatibility)

This repository is a fork of [China Set: Trains](https://github.com/OpenTTD-China-Set/China-Set-Trains)
that rebuilds the whole set at **1.15x scale**, so that China Set vehicles match
the artwork scale of the **GETS** train set (GETS sprites are drawn about 15%
larger than the default China Set scale).

The rescale is done at the source level, not by resampling the compiled GRF:

- every `.vox` model is re-rendered with `renderobject -scale 1.15` into the
  4x sprite sheets;
- all 4x sprite template rectangles and their `xrel`/`yrel` offsets are scaled
  by 1.15;
- articulated part lengths are recalculated to 1.15x (front part keeps 2 units
  so that the art offsets cancel between coupled vehicles);
- C80 (three-section hopper) gets 2/3/2 per section (21 units instead of 18),
  which stops the three sections from overlapping after the rescale.

Rebuild instructions and the scripts are in [`tools/scale115/`](tools/scale115/).

### Compatibility

- The GRF ID is unchanged (`5F5F0300`), so install it **instead of** the
  upstream China Set: Trains, never both at the same time.
- Companion forks: [China-Set-Metro-Scale115](https://github.com/WengeLiu101/China-Set-Metro-Scale115)
  and [China-Set-MTR-Addon-Scale115](https://github.com/WengeLiu101/China-Set-MTR-Addon-Scale115).
  All three use the same 1.15x scale, so they can be used together.
- Tested with OpenTTD 15.3 and 32bpp graphics.
- Rendered sprites and the compiled `.grf` are not committed (they are
  git-ignored); build them locally with the scripts above.

Everything else (vehicle stats, refits, parameters, license) is unchanged.
