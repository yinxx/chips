#-------------------------------------------------------------------------------
#   m6502_decoder.py
#   Generate instruction decoder for m6502.h emulator.
#-------------------------------------------------------------------------------
import sys

# the output path
OutPath = '../chips/_m6502_decoder.h'

# the output file handle
Out = None

# flag bits
CF = (1<<0)
ZF = (1<<1)
IF = (1<<2)
DF = (1<<3)
BF = (1<<4)
XF = (1<<5)
VF = (1<<6)
NF = (1<<7)

def flag_name(f):
    if f == CF: return 'C'
    elif f == ZF: return 'Z'
    elif f == IF: return 'I'
    elif f == DF: return 'D'
    elif f == BF: return 'B'
    elif f == XF: return 'X'
    elif f == VF: return 'V'
    elif f == NF: return 'N'

def branch_name(m, v):
    if m == NF:
        return 'BPL' if v==0 else 'BMI'
    elif m == VF:
        return 'BVC' if v==0 else 'BVS'
    elif m == CF:
        return 'BCC' if v==0 else 'BCS'
    elif m == ZF:
        return 'BNE' if v==0 else 'BEQ'

# addressing mode constants
A____ = 0       # no addressing mode
A_IMM = 1       # immediate
A_ZER = 2       # zero-page
A_ZPX = 3       # zp,X
A_ZPY = 4       # zp,Y
A_ABS = 5       # abs
A_ABX = 6       # abs,X
A_ABY = 7       # abs,Y
A_IDX = 8       # (zp,X)
A_IDY = 9       # (zp),Y
A_JMP = 10      # special JMP abs
A_JSR = 11      # special JSR abs
A_INV = 12      # an invalid instruction

# addressing mode strings
addr_mode_str = ['', '#', 'zp', 'zp,X', 'zp,Y', 'abs', 'abs,X', 'abs,Y', '(zp,X)', '(zp),Y', '', '', 'INVALID']

# memory access modes
M___ = 0        # no memory access
M_R_ = 1        # read access
M__W = 2        # write access
M_RW = 3        # read-modify-write

# addressing-modes and memory accesses for each instruction
ops = [
    # cc = 00
    [
        # ---         BIT          JMP          JMP()        STY          LDY          CPY          CPX
        [[A____,M___],[A_JSR,M_R_],[A____,M_R_],[A____,M_R_],[A_IMM,M_R_],[A_IMM,M_R_],[A_IMM,M_R_],[A_IMM,M_R_]],
        [[A_ZER,M_R_],[A_ZER,M_R_],[A_ZER,M_R_],[A_ZER,M_R_],[A_ZER,M__W],[A_ZER,M_R_],[A_ZER,M_R_],[A_ZER,M_R_]],
        [[A____,M___],[A____,M___],[A____,M__W],[A____,M___],[A____,M___],[A____,M___],[A____,M___],[A____,M___]],
        [[A_ABS,M_R_],[A_ABS,M_R_],[A_JMP,M_R_],[A_JMP,M_R_],[A_ABS,M__W],[A_ABS,M_R_],[A_ABS,M_R_],[A_ABS,M_R_]],
        [[A_IMM,M_R_],[A_IMM,M_R_],[A_IMM,M_R_],[A_IMM,M_R_],[A_IMM,M_R_],[A_IMM,M_R_],[A_IMM,M_R_],[A_IMM,M_R_]],  # relative branches
        [[A_ZPX,M_R_],[A_ZPX,M_R_],[A_ZPX,M_R_],[A_ZPX,M_R_],[A_ZPX,M__W],[A_ZPX,M_R_],[A_ZPX,M_R_],[A_ZPX,M_R_]],
        [[A____,M___],[A____,M___],[A____,M___],[A____,M___],[A____,M___],[A____,M___],[A____,M___],[A____,M___]],
        [[A_ABX,M_R_],[A_ABX,M_R_],[A_ABS,M_R_],[A_ABS,M_R_],[A_INV,M___],[A_ABX,M_R_],[A_ABX,M_R_],[A_ABX,M_R_]]        
    ],
    # cc = 01
    [
        # ORA         AND          EOR          ADC          STA          LDA          CMP          SBC
        [[A_IDX,M_R_],[A_IDX,M_R_],[A_IDX,M_R_],[A_IDX,M_R_],[A_IDX,M__W],[A_IDX,M_R_],[A_IDX,M_R_],[A_IDX,M_R_]],
        [[A_ZER,M_R_],[A_ZER,M_R_],[A_ZER,M_R_],[A_ZER,M_R_],[A_ZER,M__W],[A_ZER,M_R_],[A_ZER,M_R_],[A_ZER,M_R_]],
        [[A_IMM,M_R_],[A_IMM,M_R_],[A_IMM,M_R_],[A_IMM,M_R_],[A_IMM,M_R_],[A_IMM,M_R_],[A_IMM,M_R_],[A_IMM,M_R_]],
        [[A_ABS,M_R_],[A_ABS,M_R_],[A_ABS,M_R_],[A_ABS,M_R_],[A_ABS,M__W],[A_ABS,M_R_],[A_ABS,M_R_],[A_ABS,M_R_]],
        [[A_IDY,M_R_],[A_IDY,M_R_],[A_IDY,M_R_],[A_IDY,M_R_],[A_IDY,M__W],[A_IDY,M_R_],[A_IDY,M_R_],[A_IDY,M_R_]],
        [[A_ZPX,M_R_],[A_ZPX,M_R_],[A_ZPX,M_R_],[A_ZPX,M_R_],[A_ZPX,M__W],[A_ZPX,M_R_],[A_ZPX,M_R_],[A_ZPX,M_R_]],
        [[A_ABY,M_R_],[A_ABY,M_R_],[A_ABY,M_R_],[A_ABY,M_R_],[A_ABY,M__W],[A_ABY,M_R_],[A_ABY,M_R_],[A_ABY,M_R_]],
        [[A_ABX,M_R_],[A_ABX,M_R_],[A_ABX,M_R_],[A_ABX,M_R_],[A_ABX,M__W],[A_ABX,M_R_],[A_ABX,M_R_],[A_ABX,M_R_]]
    ],
    # cc = 02
    [
        # ASL         ROL          LSR          ROR          STX          LDX          DEC          INC
        [[A_INV,M_RW],[A_INV,M_RW],[A_INV,M_RW],[A_INV,M_RW],[A_IMM,M_R_],[A_IMM,M_R_],[A_IMM,M_R_],[A_IMM,M_R_]],
        [[A_ZER,M_RW],[A_ZER,M_RW],[A_ZER,M_RW],[A_ZER,M_RW],[A_ZER,M__W],[A_ZER,M_R_],[A_ZER,M_RW],[A_ZER,M_RW]],
        [[A____,M___],[A____,M___],[A____,M___],[A____,M___],[A____,M___],[A____,M___],[A____,M___],[A____,M___]],
        [[A_ABS,M_RW],[A_ABS,M_RW],[A_ABS,M_RW],[A_ABS,M_RW],[A_ABS,M__W],[A_ABS,M_R_],[A_ABS,M_RW],[A_ABS,M_RW]],
        [[A_INV,M_RW],[A_INV,M_RW],[A_INV,M_RW],[A_INV,M_RW],[A_INV,M__W],[A_INV,M_R_],[A_INV,M_RW],[A_INV,M_RW]],
        [[A_ZPX,M_RW],[A_ZPX,M_RW],[A_ZPX,M_RW],[A_ZPX,M_RW],[A_ZPY,M__W],[A_ZPY,M_R_],[A_ZPX,M_RW],[A_ZPX,M_RW]],
        [[A____,M_R_],[A____,M_R_],[A____,M_R_],[A____,M_R_],[A____,M___],[A____,M___],[A____,M_R_],[A____,M_R_]],
        [[A_ABX,M_RW],[A_ABX,M_RW],[A_ABX,M_RW],[A_ABX,M_RW],[A_INV,M__W],[A_ABY,M_R_],[A_ABX,M_RW],[A_ABX,M_RW]]
    ],
    # cc = 03
    [
        [[A_IDX,M_RW],[A_IDX,M_RW],[A_IDX,M_RW],[A_IDX,M_RW],[A_IDX,M__W],[A_IDX,M_R_],[A_IDX,M_RW],[A_IDX,M_RW]],
        [[A_ZER,M_RW],[A_ZER,M_RW],[A_ZER,M_RW],[A_ZER,M_RW],[A_ZER,M__W],[A_ZER,M_R_],[A_ZER,M_RW],[A_ZER,M_RW]],
        [[A_INV,M___],[A_INV,M___],[A_INV,M___],[A_INV,M___],[A_INV,M___],[A_INV,M___],[A_INV,M___],[A_IMM,M_R_]],
        [[A_ABS,M_RW],[A_ABS,M_RW],[A_ABS,M_RW],[A_ABS,M_RW],[A_ABS,M__W],[A_ABS,M_R_],[A_ABS,M_RW],[A_ABS,M_RW]],
        [[A_IDY,M_RW],[A_IDY,M_RW],[A_IDY,M_RW],[A_IDY,M_RW],[A_INV,M___],[A_IDY,M_R_],[A_IDY,M_RW],[A_IDY,M_RW]],
        [[A_ZPX,M_RW],[A_ZPX,M_RW],[A_ZPX,M_RW],[A_ZPX,M_RW],[A_ZPY,M__W],[A_ZPY,M_R_],[A_ZPX,M_RW],[A_ZPX,M_RW]],
        [[A_ABY,M_RW],[A_ABY,M_RW],[A_ABY,M_RW],[A_ABY,M_RW],[A_INV,M___],[A_INV,M___],[A_ABY,M_RW],[A_ABY,M_RW]],
        [[A_ABX,M_RW],[A_ABX,M_RW],[A_ABX,M_RW],[A_ABX,M_RW],[A_INV,M___],[A_ABY,M_R_],[A_ABX,M_RW],[A_ABX,M_RW]]
    ]
]

class opcode:
    def __init__(self, op):
        self.byte = op
        self.cmt = None
        self.src = None

#-------------------------------------------------------------------------------
#   output a src line
#
def l(s) :
    Out.write(s+'\n')

#-------------------------------------------------------------------------------
def write_defines():
    l('/* set 16-bit address in 64-bit pin mask*/')
    l('#define _SA(addr) pins=(pins&~0xFFFF)|((addr)&0xFFFFULL)')
    l('/* set 16-bit address and 8-bit data in 64-bit pin mask */')
    l('#define _SAD(addr,data) pins=(pins&~0xFFFFFF)|(((data)<<16)&0xFF0000ULL)|((addr)&0xFFFFULL)')
    l('/* set 8-bit data in 64-bit pin mask */')
    l('#define _SD(data) pins=((pins&~0xFF0000ULL)|(((data)<<16)&0xFF0000ULL))')
    l('/* extract 8-bit data from 64-bit pin mask */')
    l('#define _GD() ((uint8_t)((pins&0xFF0000ULL)>>16))')
    l('/* enable control pins */')
    l('#define _ON(m) pins|=(m)')
    l('/* disable control pins */')
    l('#define _OFF(m) pins&=~(m)')
    l('/* execute a tick */')
    l('#define _T() pins=tick(pins);ticks++')
    l('/* a memory read tick */')
    l('#define _RD() _ON(M6502_RW);_T();')
    l('/* a memory write tick */')
    l('#define _WR() _OFF(M6502_RW);_T()')
    l('/* implied addressing mode, this still puts the PC on the address bus */')
    l('#define _A_IMP() _SA(c.PC)')
    l('/* immediate addressing mode */')
    l('#define _A_IMM() _SA(c.PC++)')
    l('/* zero-page addressing mode */')
    l('#define _A_ZER() _SA(c.PC++);_RD();a=_GD();_SA(a)')
    l('/* zero page + X addressing mode */')
    l('#define _A_ZPX() _SA(c.PC++);_RD();a=_GD();_SA(a);_RD();a=(a+c.X)&0x00FF;_SA(a)')
    l('/* zero page + Y addressing mode */')
    l('#define _A_ZPY() _SA(c.PC++);_RD();a=_GD();_SA(a);_RD();a=(a+c.Y)&0x00FF;_SA(a)')
    l('/* absolute addressing mode */')
    l('#define _A_ABS() _SA(c.PC++);_RD();l=_GD();_SA(c.PC++);_RD();h=_GD();a=(h<<8)|l;_SA(a)')
    l('/* absolute+X addressing mode for read-only instructions, early out if no page boundary is crossed */')
    l('#define _A_ABX_R() _SA(c.PC++);_RD();t=_GD()+c.X;_SA(c.PC++);_RD();a=(_GD()<<8)|(t&0xFF);_SA(a);if((t&0xFF00)!=0){_RD();a=(a&0xFF00)+t;_SA(a);}')
    l('/* absolute+X addressing mode for read/write instructions */')
    l('#define _A_ABX_W() _SA(c.PC++);_RD();t=_GD()+c.X;_SA(c.PC++);_RD();a=(_GD()<<8)|(t&0xFF);_SA(a);_RD();a=(a&0xFF00)+t;_SA(a)')
    l('/* absolute+Y addressing mode for read-only instructions, early out if no page boundary is crossed */')
    l('#define _A_ABY_R() _SA(c.PC++);_RD();t=_GD()+c.Y;_SA(c.PC++);_RD();a=(_GD()<<8)|(t&0xFF);_SA(a);if((t&0xFF00)!=0){_RD();a=(a&0xFF00)+t;_SA(a);}')
    l('/* absolute+Y addressing mode for read/write instructions */')
    l('#define _A_ABY_W() _SA(c.PC++);_RD();t=_GD()+c.Y;_SA(c.PC++);_RD();a=(_GD()<<8)|(t&0xFF);_SA(a);_RD();a=(a&0xFF00)+t;_SA(a)')
    l('/* (zp,X) indexed indirect addressing mode */')
    l('#define _A_IDX() _SA(c.PC++);_RD();a=_GD();_SA(a);_RD();a=(a+c.X)&0xFF;_SA(a);_RD();t=_GD();a=(a+1)&0xFF;_SA(a);_RD();a=(_GD()<<8)|t;_SA(a);')
    l('/* (zp),Y indirect indexed addressing mode for read-only instructions, early out if no page boundary crossed */')
    l('#define _A_IDY_R() _SA(c.PC++);_RD();a=_GD();_SA(a);_RD();t=_GD()+c.Y;a=(a+1)&0xFF;_SA(a);_RD();a=(_GD()<<8)|(t&0xFF);_SA(a);if((t&0xFF00)!=0){_RD();a=(a&0xFF00)+t;_SA(a);}')
    l('/* (zp),Y indirect indexed addressing mode for read/write instructions */')
    l('#define _A_IDY_W() _SA(c.PC++);_RD();a=_GD();_SA(a);_RD();t=_GD()+c.Y;a=(a+1)&0xFF;_SA(a);_RD();a=(_GD()<<8)|(t&0xFF);_SA(a);_RD();a=(a&0xFF00)+t;_SA(a)')
    l('/* set N and Z flags depending on value */')
    l('#define _NZ(v) c.P=((c.P&~(M6502_NF|M6502_ZF))|((v&0xFF)?(v&M6502_NF):M6502_ZF))')
    l('')

#-------------------------------------------------------------------------------
def write_undefines():
    l('#undef _SA')
    l('#undef _SAD')
    l('#undef _GD')
    l('#undef _ON')
    l('#undef _OFF')
    l('#undef _T')
    l('#undef _RD')
    l('#undef _WR')
    l('#undef _A_IMP')
    l('#undef _A_IMM')
    l('#undef _A_ZER')
    l('#undef _A_ZPX')
    l('#undef _A_ZPY')
    l('#undef _A_ABS')
    l('#undef _A_ABX_R')
    l('#undef _A_ABX_W')
    l('#undef _A_ABY_R')
    l('#undef _A_ABY_W')
    l('#undef _A_IDX')
    l('#undef _A_IDY_R')
    l('#undef _A_IDY_W')

#-------------------------------------------------------------------------------
def write_interrupt_handling():
    l('    /* check for interrupt request */')
    l('    if ((pins & M6502_NMI) || ((pins & M6502_IRQ) && !(c.P & M6502_IF))) {')
    l('      /* execute a slightly modified BRK instruction */')
    l('      _RD();')
    l('      _SAD(0x0100|c.S--, c.PC>>8); _WR();')
    l('      _SAD(0x0100|c.S--, c.PC); _WR();')
    l('      _SAD(0x0100|c.S--, c.P&~M6502_BF); _WR();')
    l('      if (pins & M6502_NMI) {')
    l('        _SA(0xFFFA); _RD(); l=_GD();')
    l('        _SA(0xFFFB); _RD(); h=_GD();')
    l('      }')
    l('      else {')
    l('        _SA(0xFFFE); _RD(); l=_GD();')
    l('        _SA(0xFFFF); _RD(); h=_GD();')
    l('      }')
    l('      c.PC = (h<<8)|l;')
    l('      c.P |= M6502_IF;')
    l('      pins &= ~(M6502_IRQ|M6502_NMI);')
    l('    }')

#-------------------------------------------------------------------------------
def write_header():
    l("/* machine generated, don't edit! */")
    write_defines()
    l('uint32_t m6502_exec(m6502_t* cpu, uint32_t num_ticks) {')
    l('  m6502_t c = *cpu;')
    l('  uint8_t l, h;')
    l('  uint16_t a, t;')
    l('  uint32_t ticks = 0;')
    l('  uint64_t pins = c.PINS;')
    l('  const m6502_tick_t tick = c.tick;')
    l('  do {')
    l('    /* fetch opcode */')
    l('    _SA(c.PC++);_ON(M6502_SYNC);_RD();_OFF(M6502_SYNC);')
    l('    const uint8_t opcode = _GD();')
    l('    switch (opcode) {')

#-------------------------------------------------------------------------------
def write_footer():
    l('    }')
    write_interrupt_handling()
    l('  } while ((ticks < num_ticks) && ((pins & c.break_mask)==0));')
    l('  c.PINS = pins;')
    l('  *cpu = c;')
    l('  return ticks;')
    l('}')
    write_undefines()

#-------------------------------------------------------------------------------
def write_op(op):
    if not op.cmt:
        op.cmt = '???'
    l('      case '+hex(op.byte)+':/*'+op.cmt+'*/'+op.src+'break;')

#-------------------------------------------------------------------------------
def cmt(o,cmd):
    cc = o.byte & 3
    bbb = (o.byte>>2) & 7
    aaa = (o.byte>>5) & 7
    addr_mode = ops[cc][bbb][aaa][0]
    o.cmt = cmd;
    if addr_mode != '':
        o.cmt += ' '+addr_mode_str[addr_mode]

#-------------------------------------------------------------------------------
def u_cmt(o,cmd):
    cmt(o,cmd)
    o.cmt += ' (undoc)'

#-------------------------------------------------------------------------------
def invalid_opcode(op):
    cc = op & 3
    bbb = (op>>2) & 7
    aaa = (op>>5) & 7
    addr_mode = ops[cc][bbb][aaa][0]
    return addr_mode == A_INV

#-------------------------------------------------------------------------------
def enc_addr(op):
    # returns a string performing the addressing mode decode steps, 
    # result will be in the address bus pins
    cc = op & 3
    bbb = (op>>2) & 7
    aaa = (op>>5) & 7
    addr_mode = ops[cc][bbb][aaa][0]
    mem_access = ops[cc][bbb][aaa][1]
    if addr_mode == A____:
        # no addressing, this still puts the PC on the address bus without 
        # incrementing the PC
        src = '_A_IMP();'
    elif addr_mode == A_IMM:
        # immediate mode
        src = '_A_IMM();'
    elif addr_mode == A_ZER:
        # zero page
        src = '_A_ZER();'
    elif addr_mode == A_ZPX:
        # zero page + X
        src = '_A_ZPX();'
    elif addr_mode == A_ZPY:
        # zero page + Y
        src = '_A_ZPY();'
    elif addr_mode == A_ABS:
        # absolute
        src = '_A_ABS();'
    elif addr_mode == A_ABX:
        # absolute + X
        # this needs to check if a page boundary is crossed, which costs
        # and additional cycle, but this early-out only happens when the
        # instruction doesn't need to write back to memory
        if mem_access == M_R_:
            src = '_A_ABX_R();'
        else:
            src = '_A_ABX_W();'
    elif addr_mode == A_ABY:
        # absolute + Y
        # same page-boundary-crossed special case as absolute+X
        if mem_access == M_R_:
            src = '_A_ABY_R();'
        else:
            src = '_A_ABY_W();'
    elif addr_mode == A_IDX:
        # (zp,X)
        src = '_A_IDX();'
    elif addr_mode == A_IDY:
        # (zp),Y
        # same page-boundary-crossed special case as absolute+X
        if mem_access == M_R_:
            src = '_A_IDY_R();'
        else:
            src = '_A_IDY_W();'
    elif addr_mode == A_JMP:
        # special case JMP, partial
        src  = '_SA(c.PC++);_RD();a=_GD();_SA(c.PC++);'
    elif addr_mode == A_JSR:
        # special case JSR, partial
        src = '_SA(c.PC++);'
    else:
        # invalid instruction
        src = '';
    return src

#-------------------------------------------------------------------------------
def i_brk(o):
    cmt(o, 'BRK')
    o.src += '/*FIXME*/'

#-------------------------------------------------------------------------------
def i_nop(o):
    cmt(o,'NOP')
    o.src += '_RD();'

#-------------------------------------------------------------------------------
def u_nop(o):
    u_cmt(o,'NOP')
    o.src += '_RD();'

#-------------------------------------------------------------------------------
def i_lda(o):
    cmt(o,'LDA')
    o.src += '_RD();c.A=_GD();_NZ(c.A);'

#-------------------------------------------------------------------------------
def i_ldx(o):
    cmt(o,'LDX')
    o.src += '_RD();c.X=_GD();_NZ(c.X);'

#-------------------------------------------------------------------------------
def i_ldy(o):
    cmt(o,'LDY')
    o.src += '_RD();c.Y=_GD();_NZ(c.Y);'

#-------------------------------------------------------------------------------
def u_lax(o):
    u_cmt(o,'LAX')
    o.src += '_RD();c.A=c.X=_GD();_NZ(c.A);'

#-------------------------------------------------------------------------------
def i_sta(o):
    cmt(o,'STA')
    o.src += '_SD(c.A);_WR();'

#-------------------------------------------------------------------------------
def i_stx(o):
    cmt(o,'STX')
    o.src += '_SD(c.X);_WR();'

#-------------------------------------------------------------------------------
def i_sty(o):
    cmt(o,'STY')
    o.src += '_SD(c.Y);_WR();'

#-------------------------------------------------------------------------------
def u_sax(o):
    u_cmt(o,'SAX')
    o.src += '_SD(c.A&c.X);_WR();'

#-------------------------------------------------------------------------------
def i_tax(o):
    cmt(o,'TAX')
    o.src += '_RD();c.X=c.A;_NZ(c.X);'

#-------------------------------------------------------------------------------
def i_tay(o):
    cmt(o,'TAY')
    o.src += '_RD();c.Y=c.A;_NZ(c.Y);'

#-------------------------------------------------------------------------------
def i_txa(o):
    cmt(o,'TXA')
    o.src += '_RD();c.A=c.X;_NZ(c.A);'

#-------------------------------------------------------------------------------
def i_tya(o):
    cmt(o,'TYA')
    o.src += '_RD();c.A=c.Y;_NZ(c.A);'

#-------------------------------------------------------------------------------
def i_txs(o):
    cmt(o,'TXS')
    o.src += '_RD();c.S=c.X;'

#-------------------------------------------------------------------------------
def i_tsx(o):
    cmt(o,'TSX')
    o.src += '_RD();c.X=c.S;_NZ(c.X);'

#-------------------------------------------------------------------------------
def i_php(o):
    cmt(o,'PHP')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_plp(o):
    cmt(o,'PLP')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_pha(o):
    cmt(o,'PHA')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_pla(o):
    cmt(o,'PLA')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_se(o, f):
    cmt(o,'SE'+flag_name(f))
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_cl(o, f):
    cmt(o,'CL'+flag_name(f))
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_br(o, m, v):
    cmt(o,branch_name(m,v))
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_jmp(o):
    cmt(o,'JMP')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_jmpi(o):
    cmt(o,'JMPI')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_jsr(o):
    cmt(o,'JSR')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_rts(o):
    cmt(o,'RTS')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_rti(o):
    cmt(o,'RTI')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_ora(o):
    cmt(o,'ORA')
    o.src += '_RD();c.A|=_GD();_NZ(c.A);'

#-------------------------------------------------------------------------------
def i_and(o):
    cmt(o,'AND')
    o.src += '_RD();c.A&=_GD();_NZ(c.A);'

#-------------------------------------------------------------------------------
def i_eor(o):
    cmt(o,'EOR')
    o.src += '_RD();c.A^=_GD();_NZ(c.A);'

#-------------------------------------------------------------------------------
def i_adc(o):
    cmt(o,'ADC')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_sbc(o):
    cmt(o,'SBC')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def u_sbc(o):
    u_cmt(o,'SBC')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_cmp(o):
    cmt(o,'CMP')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_cpx(o):
    cmt(o,'CPX')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_cpy(o):
    cmt(o,'CPY')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_dec(o):
    cmt(o,'DEC')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def u_dcp(o):
    u_cmt(o,'DCP')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_dex(o):
    cmt(o,'DEX')
    o.src += '_RD();c.X--;_NZ(c.X);'

#-------------------------------------------------------------------------------
def i_dey(o):
    cmt(o,'DEY')
    o.src += '_RD();c.Y--;_NZ(c.Y);'

#-------------------------------------------------------------------------------
def i_inc(o):
    cmt(o,'INC')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_inx(o):
    cmt(o,'INX')
    o.src += '_RD();c.X++;_NZ(c.X);'

#-------------------------------------------------------------------------------
def i_iny(o):
    cmt(o,'INY')
    o.src += '_RD();c.Y++;_NZ(c.Y);'

#-------------------------------------------------------------------------------
def u_isb(o):
    u_cmt(o,'ISB')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_asl(o):
    cmt(o,'ASL')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_asla(o):
    cmt(o,'ASLA')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def u_slo(o):
    u_cmt(o,'SLO')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_lsr(o):
    cmt(o,'LSR')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_lsra(o):
    cmt(o,'LSRA')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def u_sre(o):
    u_cmt(o,'SRE')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_rol(o):
    cmt(o,'ROL')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_rola(o):
    cmt(o,'ROLA')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def u_rla(o):
    u_cmt(o,'RLA')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_ror(o):
    cmt(o,'ROR')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_rora(o):
    cmt(o,'RORA')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def u_rra(o):
    u_cmt(o,'RRA')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def i_bit(o):
    cmt(o,'BIT')
    o.src += '/* FIXME */'

#-------------------------------------------------------------------------------
def enc_op(op):
    o = opcode(op)
    if invalid_opcode(op):
        o.cmt = 'INVALID'
        o.src = ''
        return o
    # addressing mode decoder
    o.src = enc_addr(op)
    # instruction decoding
    cc = op & 3
    bbb = (op>>2) & 7
    aaa = (op>>5) & 7
    if cc == 0:
        if aaa == 0:
            if bbb == 0:        i_brk(o)
            elif bbb == 2:      i_php(o)
            elif bbb == 4:      i_br(o, NF, 0)  # BPL
            elif bbb == 6:      i_cl(o, CF)
            else:               u_nop(o)
        elif aaa == 1:
            if bbb == 0:        i_jsr(o)
            elif bbb == 2:      i_plp(o)
            elif bbb == 4:      i_br(o, NF, NF) # BMI
            elif bbb == 6:      i_se(o, CF)
            elif bbb in [5, 7]: u_nop(o)
            else:               i_bit(o)
        elif aaa == 2:
            if bbb == 0:        i_rti(o)
            elif bbb == 2:      i_pha(o)
            elif bbb == 3:      i_jmp(o)
            elif bbb == 4:      i_br(o, VF, 0)  # BVC
            elif bbb == 6:      i_cl(o, IF)
            else:               u_nop(o)
        elif aaa == 3:
            if bbb == 0:        i_rts(o)
            elif bbb == 2:      i_pla(o)
            elif bbb == 3:      i_jmpi(o)
            elif bbb == 4:      i_br(o, VF, VF) # BVS
            elif bbb == 6:      i_se(o, IF)
            else:               u_nop(o)
        elif aaa == 4:
            if bbb == 0:        u_nop(o)
            elif bbb == 2:      i_dey(o)
            elif bbb == 4:      i_br(o, CF, 0)  # BCC
            elif bbb == 6:      i_tya(o)
            else:               i_sty(o)
        elif aaa == 5:
            if bbb == 2:        i_tay(o)
            elif bbb == 4:      i_br(o, CF, CF) # BCS
            elif bbb == 6:      i_cl(o, VF)
            else:               i_ldy(o)
        elif aaa == 6:
            if bbb == 2:        i_iny(o)
            elif bbb == 4:      i_br(o, ZF, 0)  # BNE
            elif bbb == 6:      i_cl(o, DF)
            elif bbb in [5, 7]: u_nop(o)
            else:               i_cpy(o)
        elif aaa == 7:
            if bbb == 2:        i_inx(o)
            elif bbb == 4:      i_br(o, ZF, ZF) # BEQ
            elif bbb == 6:      i_se(o, DF)
            elif bbb in [5, 7]: u_nop(o)
            else:               i_cpx(o)
    elif cc == 1:
        if aaa == 0:    i_ora(o)
        elif aaa == 1:  i_and(o)
        elif aaa == 2:  i_eor(o)
        elif aaa == 3:  i_adc(o)
        elif aaa == 4:
            if bbb == 2:    u_nop(o)
            else:           i_sta(o)
        elif aaa == 5:  i_lda(o)
        elif aaa == 6:  i_cmp(o)
        else:           i_sbc(o)
    elif cc == 2:
        if aaa == 0:
            if bbb == 2:    i_asla(o)
            elif bbb == 6:  u_nop(o)
            else:           i_asl(o)
        elif aaa == 1:
            if bbb == 2:    i_rola(o)
            elif bbb == 6:  u_nop(o)
            else:           i_rol(o)
        elif aaa == 2:
            if bbb == 2:    i_lsra(o)
            elif bbb == 6:  u_nop(o)
            else:           i_lsr(o)
        elif aaa == 3:
            if bbb == 2:    i_rora(o)
            elif bbb == 6:  u_nop(o)
            else:           i_ror(o)
        elif aaa == 4:
            if bbb == 0:    u_nop(o)
            elif bbb == 2:  i_txa(o)
            elif bbb == 6:  i_txs(o)
            else:           i_stx(o)
        elif aaa == 5:
            if bbb == 2:    i_tax(o)
            elif bbb == 6:  i_tsx(o)
            else:           i_ldx(o)
        elif aaa == 6:
            if bbb == 2:        i_dex(o)
            elif bbb in [0, 6]: u_nop(o)
            else:               i_dec(o)
        elif aaa == 7:
            if bbb == 2:        i_nop(o)
            elif bbb in [0, 6]: u_nop(o)
            else:               i_inc(o)
    elif cc == 3:
        # undocumented block
        if aaa == 0:    u_slo(o)
        elif aaa == 1:  u_rla(o)
        elif aaa == 2:  u_sre(o)
        elif aaa == 3:  u_rra(o)
        elif aaa == 4:  u_sax(o)
        elif aaa == 5:  u_lax(o)
        elif aaa == 6:  u_dcp(o)
        elif aaa == 7:
            if bbb == 2:    u_sbc(o)
            else:           u_isb(o)
    return o

#-------------------------------------------------------------------------------
#   execution starts here
#
Out = open(OutPath, 'w')
write_header()

# loop over all instruction bytes
for i in range(0, 256):
    write_op(enc_op(i))
write_footer()
Out.close()
