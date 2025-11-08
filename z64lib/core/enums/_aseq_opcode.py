from z64lib.core.enums import AseqVersion
from z64lib.core.enums import VersionedIntEnum


class AseqFlowOpcode(VersionedIntEnum):
    """ Represents available audio sequence control flow opcodes. """
    RBLTZ   = 0xF2
    RBEQZ   = 0xF3
    RJUMP   = 0xF4
    BGEZ    = 0xF5
    BREAK   = 0xF6
    LOOPEND = 0xF7
    LOOP    = 0xF8
    BLTZ    = 0xF9
    BEQZ    = 0xFA
    JUMP    = 0xFB
    CALL    = 0xFC
    DELAY   = 0xFD
    DELAY1  = 0xFE
    END     = 0xFF


class AseqMetaOpcode(VersionedIntEnum):
    """ Represents available audio sequence metadata opcodes. """

    # Argbits
    TESTCHAN       = 0x00
    STOPCHAN       = 0x40
    SUBIO          = 0x50
    LDRES          = 0x60
    STIO           = 0x70
    LDIO           = 0x80
    LDCHAN         = 0x90
    RLDCHAN        = 0xA0
    LDSEQ          = 0xB0
    # Non-argbits
    C2             = (0xC2, AseqVersion.MM)
    C3             = (0xC3, AseqVersion.MM)
    RUNSEQ         = 0xC4
    SCRIPTCTR      = 0xC5
    STOP           = 0xC6
    STSEQ          = 0xC7
    SUB            = 0xC8
    AND            = 0xC9
    LDI            = 0xCC
    DYNCALL        = 0xCD
    RAND           = 0xCE
    VOICEALLOC     = 0xD0
    LDSHORTGATEARR = 0xD1
    LDSHORTVELARR  = 0xD2
    MUTEBHV        = 0xD3
    MUTE           = 0xD4
    MUTESCALE      = 0xD5
    FREECHAN       = 0xD6
    INITCHAN       = 0xD7
    VOLSCALE       = 0xD9
    VOLMODE        = 0xDA
    VOL            = 0xDB
    TEMPOCHG       = 0xDC
    TEMPO          = 0xDD
    RTRANSPOSE     = 0xDE
    TRANSPOSE      = 0xDF
    EF             = 0xEF
    FREEVOICELIST  = 0xF0
    ALLOCVOICELIST = 0xF1


class AseqChanOpcode(VersionedIntEnum):
    """ Represents available audio sequence channel opcodes. """

    # Argbits
    CDELAY         = 0x00
    LDSAMPLE       = 0x10
    LDCHAN         = 0x20
    STCIO          = 0x30
    LDCIO          = 0x40
    SUBIO          = 0x50
    LDIO           = 0x60
    STIO           = 0x70
    RLDLAYER       = 0x78
    TESTLAYER      = 0x80
    LDLAYER        = 0x88
    DELLAYER       = 0x90
    DYNLDLAYER     = 0x98
    # Non-argbits
    A0             = (0xA0, AseqVersion.MM)
    A1             = (0xA1, AseqVersion.MM)
    A2             = (0xA2, AseqVersion.MM)
    A3             = (0xA3, AseqVersion.MM)
    A4             = (0xA4, AseqVersion.MM)
    A5             = (0xA5, AseqVersion.MM)
    A6             = (0xA6, AseqVersion.MM)
    A7             = (0xA7, AseqVersion.MM)
    RANDPTR        = ((0xA8, AseqVersion.MM), (0xBD, AseqVersion.OOT))
    LDFILTER       = 0xB0
    FREEFILTER     = 0xB1
    LDSEQTOPTR     = 0xB2
    FILTER         = 0xB3
    PTRTODYNTBL    = 0xB4
    DYNTBLTOPTR    = 0xB5
    DYNTBLV        = 0xB6
    RANDTOPTR      = 0xB7
    RAND           = 0xB8
    RANDVEL        = 0xB9
    RANDGATE       = 0xBA
    CHORUS         = 0xBB
    PTRADD         = 0xBC
    SAMPLESTART    = (0xBD, AseqVersion.MM)
    UNK_BE         = (0xBE, AseqVersion.MM)
    INSTR          = 0xC1
    DYNTBL         = 0xC2
    NOLEGATO       = 0xC3
    LEGATO         = 0xC4
    DYNTBLLOOKUP   = 0xC5
    BANK           = 0xC6
    STSEQ          = 0xC7
    SUB            = 0xC8
    AND            = 0xC9
    MUTEBHV        = 0xCA
    LDSEQ          = 0xCB
    LDI            = 0xCC
    STOPCHAN       = 0xCD
    LDPTR          = 0xCE
    STPTRTOSEQ     = 0xCF
    EFFECTS        = 0xD0
    VOICEALLOC     = 0xD1
    SUSTAIN        = 0xD2
    BEND12         = 0xD3
    REVERB         = 0xD4
    VIBFREQ        = 0xD7
    VIBDEPTH       = 0xD8
    RELEASERATE    = 0xD9
    ENVELOPE       = 0xDA
    TRANSPOSE      = 0xDB
    PANWEIGHT      = 0xDC
    PAN            = 0xDD
    FREQSCALE      = 0xDE
    VOL            = 0xDF
    EXPRESSION     = 0xE0
    VIBFREQENV     = 0xE1
    VIBDEPTHENV    = 0xE2
    VIBDELAY       = 0xE3
    DYNCALL        = 0xE4
    REVERBINDEX    = 0xE5
    SAMPLEBOOK     = 0xE6
    LOADPARAMS     = 0xE7
    PARAMS         = 0xE8
    VOICEPRIO      = 0xE9
    STOP           = 0xEA
    BANKINSTR      = 0xEB
    VIBRESET       = 0xEC
    GAIN           = 0xED
    BEND2          = 0xEE
    FREEVOICELIST  = 0xF0
    ALLOCVOICELIST = 0xF1


class AseqLayerOpcode(VersionedIntEnum):
    """ Represents available audio sequence note layer opcodes. """
    NOTEDVG      = 0x00
    NOTEDV       = 0x40
    NOTEVG       = 0x80
    LDELAY       = 0xC0
    SHORTVEL     = 0xC1
    TRANSPOSE    = 0xC2
    SHORTDELAY   = 0xC3
    LEGATO       = 0xC4
    NOLEGATO     = 0xC5
    INSTR        = 0xC6
    PORTAMENTO   = 0xC7
    NOPORTAMENTO = 0xC8
    SHORTGATE    = 0xC9
    NOTEPAN      = 0xCA
    ENVELOPE     = 0xCB
    NODRUMPAN    = 0xCC
    STEREO       = 0xCD
    BEND2        = 0xCE
    RELEASERATE  = 0xCF
    # Argbits
    LDSHORTVEL   = 0xD0
    LDSHORTGATE  = 0xE0
    # Non-argbits
    F0           = 0xF0
    F1           = 0xF1