# Ace3DS

This cart goes by a few names, including:

* Ace3DS Plus
* Ace3DS X (has a switch for ntrboot mode)
* r4isdhc.com.cn
* Gateway Blue (not all Gateway Blues, though)

## Cart commands

All (?) non-standard commands are ignored when anti-antipiracy is active, returning zeros or `FF`s.

### `B0 00 00 00 00 00 00 00`

Response: 4 bytes

When treated as an 32-bit little endian integer `0xFFHH00SS`

* `FF` is a binary-coded decimal representing the "firmware version"

  e.g. `22` means firmware 2.2

* `HH` is a BCD representing the "hardware version"

  e.g. `A0` means hardware 10.0

* `SS` is some sort of status register, used in SD init and likely elsewhere

### `B9 xx xx xx xx 00 00 00`

Response: 4 bytes

Reads a 0x200-byte sector off the SD. This command should be repeated until the response is zero, and then the response can be read via command `BA`.

### `BA 00 00 00 00 00 00 00`

Response: 512 bytes

Read the FPGA's internal SD buffer, e.g. from `B9` or `C0`.

### `BF xx xx xx xx 00 00 00`

Response: 512 bytes

Read the FPGA's internal SD buffer, decrypted using a modified R4 bitshuffling cipher (the key is XORed with the block index), with key 0x4002. Used by the kernel to read `_DSMENU.DAT` off the SD.

### `C0 xx yy yy yy yy zz 00`

Response: 0 bytes

Sends a raw SD command `x` with parameter `y` and flags (?) `z`.

The command progress can be polled via `B0`.

The SD's response is stored somewhere in the FPGA, and can be read via command `BA`.

### `C2 00 00 00 xx 00 00 00`

Response: 0 bytes

Used in SD init.

### `C6 00 00 00 00 00 00 00`

Response: 512 bytes

Returns some random byte string, or all zeroes. (?)

Used to enable access to the cart's flash via SPI.

### `C7 5A 55 AA A5 3C FF C3`

Expects: 512 bytes

The official Ace3DS updaters do some bitshuffling with the response of `C6`, and then return it to the cart here. After this command, the cart's firmware flash is accessible over SPI (instead of the save flash).

## Flash data

A script to convert a flash dump to an NDS file is [here](https://github.com/ntrteam/docs/blob/master/ace3ds/nor2rom.py).

The first 0x8000 bytes contain two arrays of 8192 16-bit integers; the first is the ROM to flash map used after anti-antipiracy is deactivated, and the second is the map used before it is deactivated.

`nor_address(rom_address) = (map[rom_address >> 12] << 12) + (rom_address & 0xFFF)`

The blowfish S boxes are located at 0x8000, and the 18 integer P array is located at 0x9000 in reverse order.

At 0x9050 there is some version string and date

```
0x9050    46 4C 41 53 48 20 47 45 4E 20 56 34 2E 30 00 FF    FLASH GEN V4.0
0x9060    42 79 20 4B 45 4E 00 FF FF FF FF FF FF FF FF FF    By KEN
0x9070    32 30 31 32 2F 31 30 2F 32 00 FF FF 00 D0 16 00    2012/10/2
```

followed by the chip ID and version

```
0x9080    C2 0F 00 00 00 00 32 18 FF FF FF FF FF FF FF FF
```

At 0x90C0 there is some sort of configuration for the anti-antipiracy:

<pre>
<strong>C1 15 94 10 C0 0B 74 F0</strong> C3 DF 20 7E E2 C7 4C 00
53 45 54 00 53 54 4F 50 02 38 00 00 02 00 40 00
53 45 54 00 53 54 41 52 02 7F E0 00 02 7F F4 00
10 10 8D E5 BE 10 DE EF 00 00 00 00 00 00 00 FF
</pre>

The bolded portion corresponds to `B7` reads to 0x1159400 and 0xB7400, in that order, needed to deactivate anti-antipiracy. The meaning of the rest of the block is unknown.

The Ace3DS X's NTRboot flash has this entire section replaced by 0xFFFFFFF0, which appears to disable the anti-antipiracy.

The rest of the flash, from 0xA000 onwards, is used for game data.

## Initialisation

The cart needs to be brought into KEY2, and the appropriate `B7` reads need to be done to enable the cart commands. (There is no way to guess which addresses need to be read.)

The cart's SD needs to be initialised and a `B9` SD read successfully completed before the cart will respond to SPI. The `C6` and `C7` commands need to be sent to switch the SPI to the firmware flash.

Once that is done, the flash can be modified using typical SPI commands.