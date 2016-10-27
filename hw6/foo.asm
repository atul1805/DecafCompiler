# preamble 
.text
main_entry_point:
subu $sp, $sp, 32
sw $ra, 28($sp)
sw $fp, 24($sp)
addu $fp, $sp, 32
li $t9, 25
sw $t8, 24($sp)
move $a0, $t9
jal M_fact_7
move $a0, $v0
move $t3, $a0
lw $t8, 24($sp)
move $t8, $t3
li $v0, 10
syscall

M_fact_7:
subu $sp, $sp, 60
sw $ra, 56($sp)
sw $fp, 52($sp)
addu $fp, $sp, 60
li $t8, 2
sle $t9, $a0, $t8
beqz $t9, L_0
li $t2, 1
move $a0, $t2
move $v0, $a0
lw $ra, 56($sp)
lw $fp, 52($sp)
addu $sp, $sp, 60
jr $ra
j L_1
L_0:
li $t3, 1
sub $t0, $a0, $t3
sw $t8, 52($sp)
sw $t9, 48($sp)
sw $t2, 44($sp)
sw $a0, 40($sp)
move $a0, $t0
jal M_fact_7
move $a0, $v0
move $t1, $a0
lw $t2, 44($sp)
lw $t9, 48($sp)
lw $t8, 52($sp)
lw $a0, 40($sp)
li $t6, 2
sub $t7, $a0, $t6
sw $t8, 36($sp)
sw $t9, 32($sp)
sw $t2, 28($sp)
sw $t3, 24($sp)
sw $t0, 20($sp)
sw $t1, 16($sp)
sw $a0, 12($sp)
move $a0, $t7
jal M_fact_7
move $a0, $v0
move $t4, $a0
lw $t1, 16($sp)
lw $t0, 20($sp)
lw $t3, 24($sp)
lw $t2, 28($sp)
lw $t9, 32($sp)
lw $t8, 36($sp)
lw $a0, 12($sp)
add $t5, $t1, $t4
move $a0, $t5
move $v0, $a0
lw $ra, 56($sp)
lw $fp, 52($sp)
addu $sp, $sp, 60
jr $ra
L_1:

