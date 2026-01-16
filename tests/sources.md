# Test file origin

The files in the sample directory have been sourced in the following ways:

| **Hash**                                                         | **Description**                                                                                                                 | **Source**     |
| ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | -------------- |
| test0.exe | A simple C program that prints out a key `!UNPACK_KEY! a007be07-5ca3-421f-85b1-05befc9fe113 !UNPACK_KEY!` This sample is then packed using UPX to obfuscate the key. The respective test case works by applying unipacker to this sample and searching for the unpacked key in the blob output. | Self generated: See `samples-src` directory. |
