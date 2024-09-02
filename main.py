import asyncio
import aiopoke
import json
from collections import Counter
import aiopoke.utils
import os
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


async def get_pokemon_names() -> list[str]:
    client = aiopoke.AiopokeClient()
    english = await client.get_language(name_or_id="en")
    pokemon_list = await asyncio.gather(
        *[client.get_pokemon(i) for i in range(1, 1025)]
    )
    pokemon_form_names_list = fetch_pokemon_form_names(english, pokemon_list)

    pokemon_species_list = await asyncio.gather(
        *[pokemon.species.fetch() for pokemon in pokemon_list]
    )

    pokemon_names_list = [
        name.name
        for species in pokemon_species_list
        for name in species.names
        if name.language.id == english.id
    ]
    return pokemon_names_list + await pokemon_form_names_list


async def fetch_pokemon_form_names(english, pokemon_list):
    pokemon_form_names_list = [
        name.name
        for pokemon in pokemon_list
        for minimal_form in pokemon.forms
        for form in [await minimal_form.fetch()]
        for name in form.names
        if name.language.id == english.id
    ]

    return pokemon_form_names_list


async def main() -> None:
    if os.path.exists("pokemon_names.json"):
        with open("pokemon_names.json", "r", encoding="utf-8") as f:
            pokemon_names_list: list[str] = json.load(f)
        print(f"Loaded {len(pokemon_names_list)} pokemon names")
    else:
        pokemon_names_list = await get_pokemon_names()
        with open("pokemon_names.json", "w", encoding="utf-8") as f:
            json.dump(pokemon_names_list, f, indent=2, ensure_ascii=False)
        print(f"Fetched {len(pokemon_names_list)} pokemon names")

    while True:
        scrambed = input("Enter the scrambled word: ")
        result = anagram_check(scrambed, pokemon_names_list)
        for index, (word, score) in enumerate(result[:10]):
            print(f"{index + 1}. {word} @ {score:.2f}")


asyncio.run(main())
