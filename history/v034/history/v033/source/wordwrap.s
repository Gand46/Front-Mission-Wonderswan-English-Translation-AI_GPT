.intel_syntax noprefix
.code16
.section .text
.global scan_word, primary_check, secondary_advance, secondary_check

# Bank 76: replace only the old post-glyph boundary checks.
.org 0xd233
secondary_check:
    pusha
    push ds
    mov si, di
    add si, bx
    shl dx, 1
    test byte ptr ss:[0x3fd6], 1
    jz sec_capacity
    inc dx
sec_capacity:
    mov cx, 44
    cmp byte ptr ss:[0x3fce], 0x10
    je sec_scan
    mov cx, 30
sec_scan:
    # During FC name expansion the main cursor is not the glyph cursor.
    # Do not consume a main-text space until expansion has finished.
    cmp byte ptr ss:[0x3fc4], 4
    je sec_dynamic
    cmp byte ptr ss:[0x3fc4], 7
    je sec_dynamic
    call scan_word
    jnc sec_done
    jmp sec_wrap
sec_dynamic:
    xor ax, ax
    cmp dx, cx
    jb sec_done
sec_wrap:
    add word ptr ss:[0x3fc0], ax
    pop ds
    popa
    call 0xd51c
    jmp 0xd2ce
sec_done:
    pop ds
    popa
    jmp 0xd2ce
.org 0xd2ce, 0x90

# Verified FF tail padding at bank 76, bounded to FEA4..FFFF.
.org 0xfea4
# Input DS:SI = next token; DX = x/4, CX = capacity/4.
# CF=1 requests a line/page transition; AX = leading-space bytes to skip.
# No text rewrite. A token longer than the window retains hard-limit fallback.
scan_word:
    xor ax, ax
    mov bl, [si]
    cmp bl, 0xf8
    jae no_wrap
    cmp dx, cx
    jae hard_wrap
    mov di, dx
    cmp bl, 0xbb
    je space_one
    cmp word ptr [si], 0x3fc0
    jne no_wrap
    mov ax, 2
    add di, 2
    jmp scan_start
space_one:
    inc ax
    inc di
scan_start:
    add si, ax
    mov bp, 64
scan_loop:
    mov bl, [si]
    cmp bl, 0xf8
    jae measured
    cmp bl, 0xbb
    je measured
    cmp word ptr [si], 0x3fc0
    je measured
    inc si
    cmp bl, 0xc0
    jb single_byte
    inc si
    add di, 2
    jmp width_added
single_byte:
    inc di
    cmp bl, 0xbb
    jb wide_single
    cmp bl, 0xbf
    jbe width_added
wide_single:
    inc di
width_added:
    cmp di, cx
    ja yes_wrap
    dec bp
    jnz scan_loop
measured:
    cmp di, cx
    ja yes_wrap
no_wrap:
    clc
    ret
hard_wrap:
    cmp bl, 0xbb
    jne hard_legacy
    inc ax
    jmp yes_wrap
hard_legacy:
    cmp word ptr [si], 0x3fc0
    jne yes_wrap
    mov ax, 2
yes_wrap:
    stc
    ret

# Far-call entry from bank 78; preserve the protected name-entry cadence.
primary_check:
    pusha
    push ds
    cmp byte ptr ss:[0x09b9], 0xb0
    jne primary_text
    cmp word ptr ss:[0x09ba], 0x7698
    jae primary_text
    cmp byte ptr ss:[0x09bf], 22
    jb primary_no
    jmp primary_yes
primary_text:
    xor dx, dx
    mov dl, ss:[0x09bf]
    shl dx, 1
    test byte ptr ss:[0x09bc], 0x20
    jz primary_pos
    inc dx
primary_pos:
    mov ds, ss:[0x09b8]
    mov si, ss:[0x09ba]
    mov cx, 44
    call scan_word
    jnc primary_no
    add word ptr ss:[0x09ba], ax
primary_yes:
    pop ds
    popa
    stc
    retf
primary_no:
    pop ds
    popa
    clc
    retf

# Normal glyph paths advance one tile; narrow aliases advance half a tile.
# FD special-width operators retain their original phase toggle.
secondary_advance:
    pusha
    push ds
    mov ds, ss:[0x3fb8]
    mov si, ss:[0x3fba]
    add si, ss:[0x3fc0]
    cmp byte ptr [si-2], 0xfd
    je phase_toggle
    cmp byte ptr ss:[0x3fc4], 4
    je advance_done
    cmp byte ptr ss:[0x3fc4], 7
    je advance_done
    mov al, [si-1]
    sub al, 0xbb
    cmp al, 4
    ja advance_done
    cmp byte ptr [si-2], 0xc0
    jb narrow_advance
    cmp byte ptr [si-2], 0xf8
    jb advance_done
narrow_advance:
    xor byte ptr ss:[0x3fd6], 1
    test byte ptr ss:[0x3fd6], 1
    jz advance_done
    dec word ptr ss:[0x3fc2]
    jmp advance_done
phase_toggle:
    xor byte ptr ss:[0x3fd6], 1
advance_done:
    pop ds
    popa
    ret
.global patch_end
patch_end:
