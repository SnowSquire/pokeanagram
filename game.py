import json
from collections import Counter
import re


def similarity(word1: str, word2: str) -> float:
    d1 = Counter(sanitize_names(word1))
    d2 = Counter(sanitize_names(word2))
    d2.subtract(d1)
    total = sum([abs(val) for val in d2.values()]) / len(d2)
    return total


def anagram_check(word: str, word_list: list[str]) -> list[tuple[str, float]]:
    anagram_scores: dict[str, float] = {}
    for word2 in word_list:
        score = similarity(word, word2)
        anagram_scores[word2] = score
    return sorted(anagram_scores.items(), key=lambda x: x[1])


def sanitize_names(word: str) -> str:
    regex = re.compile("[^a-zA-Z]")
    return regex.sub("", word.lower())


def main() -> None:
    with open("pokemon_names.json", "r", encoding="utf-8") as f:
        pokemon_names_list: list[str] = json.load(f)
    print(f"Loaded {len(pokemon_names_list)} pokemon names")

    while True:
        scrambed = input("Enter the scrambled word: ")
        result = anagram_check(scrambed, pokemon_names_list)
        for index, (word, score) in enumerate(result[:10]):
            print(f"{index + 1}. {word} @ {score:.2f}")


main()
