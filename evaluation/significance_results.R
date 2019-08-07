# Title     : TODO
# Objective : TODO
# Created by: jagfelga
# Created on: 16.07.18
#!/usr/bin/env Rscript

args = commandArgs(trailingOnly=TRUE)

sys_results_file = args[1]
results <- read.csv2(sys_results_file, sep = ';', header = T, dec='.')

human_results_file = args[2]
results_human <- read.csv2(human_results_file, sep = ';', header = T, dec='.')

print("Test set BLEU")
wilcox.test(results$test_word_BLEU, results$test_char_BLEU, paired = FALSE)

print("Test set ROUGE")
wilcox.test(results$test_word_ROUGE, results$test_char_ROUGE, paired = FALSE)

print("Dev set BLEU word vs char")
wilcox.test(results$dev_word_BLEU, results$dev_char_BLEU, paired = FALSE)

print("Dev set ROUGE word vs char")
wilcox.test(results$dev_word_ROUGE, results$dev_char_ROUGE, paired = FALSE)

print("Dev set BLEU human vs char")
wilcox.test(results_human$dev_human_BLEU, results$dev_char_BLEU, paired = FALSE)

print("Dev set ROUGE human vs char")
wilcox.test(results_human$dev_human_ROUGE, results$dev_char_ROUGE, paired = FALSE)

print("Dev set BLEU human vs word")
wilcox.test(results_human$dev_human_BLEU, results$dev_word_BLEU, paired = FALSE)

print("Dev set ROUGE human vs word")
wilcox.test(results_human$dev_human_ROUGE, results$dev_word_ROUGE, paired = FALSE)

print("Dev set diversity")
print("Word vs char")
print("Unique texts")
wilcox.test(results$dev_word_uniq_texts, results$dev_char_uniq_texts, paired = FALSE)
print("Unique sentences")
wilcox.test(results$dev_word_uniq_sents, results$dev_char_uniq_sents, paired = FALSE)
print("Unique words")
wilcox.test(results$dev_word_uniq_words, results$dev_char_uniq_words, paired = FALSE)
print("New texts")
wilcox.test(results$dev_word_new_texts, results$dev_char_new_texts, paired = FALSE)
print("New sentences")
wilcox.test(results$dev_word_new_sents, results$dev_char_new_sents, paired = FALSE)

print("Human vs char")
print("Unique texts")
wilcox.test(results_human$dev_human_uniq_texts, results$dev_char_uniq_texts, paired = FALSE)
print("Unique sentences")
wilcox.test(results_human$dev_human_uniq_sents, results$dev_char_uniq_sents, paired = FALSE)
print("Unique words")
wilcox.test(results_human$dev_human_uniq_words, results$dev_char_uniq_words, paired = FALSE)
print("New texts")
wilcox.test(results_human$dev_human_new_texts, results$dev_char_new_texts, paired = FALSE)
print("New sentences")
wilcox.test(results_human$dev_human_new_sents, results$dev_char_new_sents, paired = FALSE)

print("Human vs word")
print("Unique texts")
wilcox.test(results_human$dev_human_uniq_texts, results$dev_word_uniq_texts, paired = FALSE)
print("Unique sentences")
wilcox.test(results_human$dev_human_uniq_sents, results$dev_word_uniq_sents, paired = FALSE)
print("Unique words")
wilcox.test(results_human$dev_human_uniq_words, results$dev_word_uniq_words, paired = FALSE)
print("New texts")
wilcox.test(results_human$dev_human_new_texts, results$dev_word_new_texts, paired = FALSE)
print("New sentences")
wilcox.test(results_human$dev_human_new_sents, results$dev_word_new_sents, paired = FALSE)