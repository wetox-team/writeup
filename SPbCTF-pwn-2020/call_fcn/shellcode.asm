BITS 64
global _start

_start:
	xor rdx, rdx
	xor rsi, rsi
	
	mov rdi, 0x6010b0
	mov dword [rdi], 0xcafebabe

	mov rdi, 0x4006B0
	call rdi

	ret