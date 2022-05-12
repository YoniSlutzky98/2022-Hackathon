from difflib import SequenceMatcher
import tika, os, re
from tika import parser
from collections import Counter
tika.initVM()

def find_noisy_words(path):
        word_counts = dict()
        for f in os.listdir(path):
            parsed = parser.from_file(path + f)
            c = Counter(parsed["content"].replace('\n',"").split(" "))
            for word in c:
                if word not in word_counts:
                    word_counts[word] = 0
                word_counts[word] += c[word]
        bar = 10 ## Rethink?
        return [word for word in word_counts if word_counts[word] > bar]

def clean(text, noisy_words):
    text = [x.split(" ") for x in text if len(x)>=20]
    text = [[w for w in x if w not in noisy_words] for x in text]
    text = [[w for w in x if w != ''] for x in text]
    return text

def parse(path, noisy_words):
    parsed = tika.parser.from_file(path)
    text = re.split('שאלה|תשובה', parsed["content"].replace('\n',""))
    return clean(text, noisy_words)

def find_score(new_pdf_lst, old_pdf_lst): # Return score of old_pdf_lst
    scores = [0 for i in range(len(new_pdf_lst))]
    for i, new_sent in enumerate(new_pdf_lst):
        for old_sent in old_pdf_lst:
            if SequenceMatcher(None, new_sent, old_sent).ratio() > 0.5:
                scores[i] += 1
                break
    return sum(scores) / len(scores)


new_assignment_path = 'Ex4.pdf'
old_assignments_path = '0368-2159 מבנה מחשבים\Homework\\2022\סמסטר א_\\'
noisy_words = find_noisy_words(old_assignments_path)
new_pdf_lst = parse(new_assignment_path, noisy_words)

paths = []
scores = []
for f in os.listdir(old_assignments_path):
    paths.append(f)
    old_pdf_lst = parse(old_assignments_path + f, noisy_words)
    scores.append(find_score(new_pdf_lst, old_pdf_lst))
avg_score = sum(scores) / len(scores)
significant = [(paths[i], scores[i]) for i in range(len(scores)) if scores[i] > 0]
significant.sort(key = lambda x: x[1], reverse= True)
print(significant)