from z64lib.ultratypes import *


#region EnvelopePoint
# Envelopes are a special struct array type that are handled
# by effects.c with Audio_AdsrUpdate()/AudioEffects_UpdateAdsr()
# parsing the envelope points to adjust the amplitude of the
# audio signal during audio sequence playback
class EnvelopePoint(structure):
    """
    #### Attributes
    `delay` : s16
    `arg` : s16

    #### ZeldaRET Decompilation
    ```c
    typedef struct EnvelopePoint {
        /* 0x0 */ signed short int delay;
        /* 0x2 */ signed short int arg;
    } EnvelopePoint; // size = 0x4
    ```
    """
    _members_ = [
        ('delay', s16),
        ('arg', s16),
    ] # Size = 0x4
#endregion


#region VadpcmLoopHeader
# 'num_samples' is used with looping samples to indicate the true end
# of the sample data, otherwise 'count' is used as the end of the sample
class VadpcmLoopHeader(structure):
    """
    #### Attributes:
    `start` : u32
    `end` : u32
    `count` : u32
    `num_samples` : u32

    #### ZeldaRET Decompilation
    ```c
    typedef struct AdpcmLoopHeader {
        /* 0x00 */ unsigned long start;
        /* 0x04 */ unsigned long end;
        /* 0x08 */ unsigned long count;
        /* 0x0C */ unsigned long numSamples;
    } AdpcmLoopHeader; // size = 0x10
    ```
    """
    _members_ = [
        ('start', u32),
        ('end', u32),
        ('count', u32),
        ('num_samples', u32),
    ] # Size = 0x10
#endregion


#region VadpcmLoop
# If 'header.count' is equal to 0, then 'predictors' is ignored
class VadpcmLoop(structure):
    """
    #### Attributes
    `header` : VadpcmLoopHeader
    `predictors` : array[s16, 16]

    #### ZeldaRET Decompilation
    ```c
    typedef struct AdpcmLoop {
        /* 0x00 */ AdpcmLoopHeader header;
        /* 0x10 */ signed short int predictors[16];
    } AdpcmLoop; // size = 0x30 (or 0x10)
    ```
    """
    _members_ = [
        ('header', VadpcmLoopHeader),
        ('predictors', array[s16, 16]),
    ] # Size = 0x10 or 0x30
#endregion


#region VadpcmBookHeader
class VadpcmBookHeader(structure):
    """
    #### Attributes
    `order` : s32
    `num_predictors` : s32

    #### ZeldaRET Decompilation
    ```c
    typedef struct AdpcmBookHeader {
        /* 0x00 */ signed long order;
        /* 0x04 */ signed long numPredictors;
    } AdpcmBookHeader; // size = 0x8
    ```
    """
    _members_ = [
        ('order', s32),
        ('num_predictors', s32),
    ] # Size = 0x8
#endregion


#region VadpcmBook
class VadpcmBook(structure):
    """
    #### Attributes
    `header` : VadpcmBookHeader
    `predictors` : array[s16]

    #### ZeldaRET Decompilation
    ```c
    typedef struct AdpcmBook {
        /* 0x00 */ AdpcmBookHeader header;
        /* 0x08 */ signed short int predictors[];
    } AdpcmBook; // size >= 0x8
    ```
    """
    _members_ = [
        ('header', VadpcmBookHeader),
        ('predictors', array[s16]), # 8 * order * num_predictors
    ] # Size = 0x8 + FAM length
#endregion


#region Sample
# 'sample_addr' is a pointer to the actual compressed VADPCM data in
# the audio table
class Sample(structure):
    """
    #### Attributes
    `flags` : bitfield[u32]
    `codec` : u32
    `medium` : u32
    `is_cached` : u32
    `is_relocated` : u32
    `size` : u32
    `sample_addr` : pointer[u8]
    `loop` : pointer[VadpcmLoop]
    `book` : pointer[VadpcmBook]

    #### ZeldaRET Decompilation
    ```c
    typedef struct Sample {
        /* 0x00 */ unsigned long codec : 4;
        /* 0x00 */ unsigned long medium : 2;
        /* 0x00 */ unsigned long isCached : 1;
        /* 0x00 */ unsigned long isRelocated : 1;
        /* 0x01 */ unsigned long size : 24;
        /* 0x04 */ unsigned char* sampleAddr;
        /* 0x08 */ AdpcmLoop* loop;
        /* 0x0C */ AdpcmBook* book;
    } Sample; // size = 0x10
    ```
    """
    _members_ = [
        ('flags', bitfield[u32, [
            ('codec', 4),
            ('medium', 2),
            ('is_cached', 1),
            ('is_relocated', 1),
            ('size', 24),
        ]]),
        ('sample_addr', pointer[u8]),
        ('loop', pointer[VadpcmLoop]),
        ('book', pointer[VadpcmBook]),
    ] # Size = 0x10
#endregion


#region TunedSample
class TunedSample(structure):
    """
    #### Attributes
    `sample` : pointer[Sample]
    `tuning` : f32

    #### ZeldaRET Decompilation
    ```c
    typedef struct TunedSample {
        /* 0x00 */ Sample* sample;
        /* 0x04 */ float tuning;
    } TunedSample; // size = 0x8
    ```
    """
    _members_ = [
        ('sample', pointer[Sample]),
        ('tuning', f32),
    ] # Size = 0x8
#endregion


#region Instrument
class Instrument(structure):
    """
    #### Attributes
    `is_relocated` : u8
    `key_region_split_1` : u8
    `key_region_split_2` : u8
    `decay_index` : u8
    `envelope` : pointer[EnvelopePoint]
    `low_region_sample` : pointer[TunedSample]
    `prim_region_sample` : pointer[TunedSample]
    `high_region_sample` : pointer[TunedSample]

    #### ZeldaRET Decompilation
    ```c
    typedef struct Instrument {
        /* 0x00 */ unsigned char isRelocated;
        /* 0x01 */ unsigned char normalRangeLo;
        /* 0x02 */ unsigned char normalRangeHi;
        /* 0x03 */ unsigned char adsrDecayIndex;
        /* 0x04 */ EnvelopePoint* envelope;
        /* 0x08 */ TunedSample lowPitchTunedSample;
        /* 0x10 */ TunedSample normalPitchTunedSample;
        /* 0x18 */ TunedSample highPitchTunedSample;
    } Instrument; // size = 0x20
    ```
    """
    _members_ = [
        ('is_relocated', u8),
        ('key_region_split_1', u8),
        ('key_region_split_2', u8),
        ('decay_index', u8),
        ('envelope', pointer[EnvelopePoint]),
        ('low_region_sample', pointer[TunedSample]),
        ('prim_region_sample', pointer[TunedSample]),
        ('high_region_sample', pointer[TunedSample]),
    ] # Size = 0x20
#endregion


#region Drum
# If 'tuned_sample' or 'tuned_sample.sample' is null,
# then the game/audio engine crashes. When parsing/creating
# a Drum, add checks to ensure that 'tuned_sample' and
# 'tuned_sample.sample' is not null or overflows
class Drum(structure):
    """
    #### Attributes
    `decay_index` : u8
    `pan` : u8
    `is_relocated` : u8
    `tuned_sample` : pointer[TunedSample]
    `envelope` : pointer[EnvelopePoint]

    #### ZeldaRET Decompilation
    ```c
    typedef struct Drum {
        /* 0x00 */ unsigned char adsrDecayIndex;
        /* 0x01 */ unsigned char pan;
        /* 0x02 */ unsigned char isRelocated;
        /* 0x04 */ TunedSample tunedSample;
        /* 0x0C */ EnvelopePoint* envelope;
    } Drum; // size = 0x10
    ```
    """
    _field_ = [
        ('decay_index', u8),
        ('pan', u8),
        ('is_relocated', u8),
        ('tuned_sample', pointer[TunedSample]),
        ('envelope', pointer[EnvelopePoint]),
    ] # Size = 0x10
#endregion


#region SoundEffect
# Pointless TunedSample wrapper class
class SoundEffect(structure):
    """
    #### Attributes
    `tuned_sample` : pointer[TunedSample]

    #### ZeldaRET Decompilation
    ```c
    typedef struct SoundEffect {
        /* 0x00 */ TunedSample tunedSample;
    } SoundEffect; // size = 0x08
    ```
    """
    _members_ = [
        ('tuned_sample', pointer[TunedSample])
    ] # Size = 0x8
#endregion


#region SoundFont
# SoundFont is a misnomer
class SoundFont(structure):
    """
    #### Attributes
    `num_instruments` : u8
    `num_drums` : u8
    `sample_bank_1` : u8
    `sample_bank_2` : u8
    `num_effects` : u16
    `instruments` : pointer[pointer[Instrument]]
    `drums` : pointer[pointer[Drum]]
    `effects` : pointer[SoundEffect]

    #### ZeldaRET Decompilation
    ```c
    typedef struct SoundFont {
        /* 0x00 */ unsigned char numInstruments;
        /* 0x01 */ unsigned char numDrums;
        /* 0x02 */ unsigned char sampleBankId1;
        /* 0x03 */ unsigned char sampleBankId2;
        /* 0x04 */ unsigned short int numSfx;
        /* 0x08 */ Instrument** instruments;
        /* 0x0C */ Drum** drums;
        /* 0x10 */ SoundEffect* soundEffects;
    } SoundFont; // size = 0x14
    ```
    """
    _members_ = [
        ('num_instruments', u8),
        ('num_drums', u8),
        ('sample_bank_1', u8),
        ('sample_bank_2', u8),
        ('num_effects', u16),
        ('instruments', pointer[[pointer[Instrument]]]),
        ('drums', pointer[[pointer[Drum]]]),
        ('effects', pointer[SoundEffect]),
    ] # Size = 0x14
#endregion


#region AudioTableHeader
class AudioTableHeader(structure):
    """
    #### Attributes
    `num_entries` : s16
    `unk_medium_param` : s16
    `rom_addr` : u32
    `pad` : array[u8, 8]

    #### ZeldaRET Decompilation
    ```c
    typedef struct AudioTableHeader {
        /* 0x00 */ signed short int numEntries;
        /* 0x02 */ signed short int unkMediumParam;
        /* 0x04 */ uintptr_t romAddr;
        /* 0x08 */ char pad[0x8];
    } AudioTableHeader; // size = 0x10
    ```
    """
    _members_ = [
        ('num_entries', s16),
        ('unk_medium_param', s16),
        ('rom_addr', u32),
        ('pad', array[u8, 8]),
    ] # Size = 0x10
#endregion


#region AudioTableEntry
class AudioTableEntry(structure):
    """
    #### Attributes
    `rom_addr` : u32
    `size` : u32
    `medium` : s8
    `cache_policy` : s8
    `short_data_1` : s16
    `short_data_2` : s16
    `short_data_3` : s16

    #### ZeldaRET Decompilation
    ```c
    typedef struct AudioTableEntry {
        /* 0x00 */ unsigned long romAddr;
        /* 0x04 */ unsigned long size;
        /* 0x08 */ signed char medium;
        /* 0x09 */ signed char cachePolicy;
        /* 0x0A */ signed short int shortData1;
        /* 0x0C */ signed short int shortData2;
        /* 0x0E */ signed short int shortData3;
    } AudioTableEntry; // size = 0x10
    ```
    """
    _members_ = [
        ('rom_addr', u32),
        ('size', u32),
        ('medium', s8),
        ('cache_policy', s8),
        ('short_data_1', s16),
        ('short_data_2', s16),
        ('short_data_3', s16),
    ] # Size = 0x10
#endregion


#region AudioTable
class AudioTable(structure):
    """
    #### Attributes
    `header` : AudioTableHeader
    `entries` : array[AudioTableEntry]

    #### ZeldaRET Decompilation
    ```c
    typedef struct AudioTable {
        /* 0x00 */ AudioTableHeader header;
        /* 0x10 */ AudioTableEntry entries[];
    } AudioTable; // size >= 0x20
    ```
    """
    _members_ = [
        ('header', AudioTableHeader),
        ('entries', array[AudioTableEntry]),
    ] # Size >= 0x20
#endregion