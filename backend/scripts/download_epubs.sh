#!/bin/bash
# Download EPUB files for the 50 new books from Project Gutenberg
# Run from the project root: bash backend/scripts/download_epubs.sh

BOOKS_DIR="$(dirname "$0")/../../books"
mkdir -p "$BOOKS_DIR"

download_epub() {
    local slug="$1"
    local gutenberg_id="$2"
    local dest="$BOOKS_DIR/${slug}.epub"

    if [ -f "$dest" ]; then
        echo "  SKIP: ${slug}.epub already exists"
        return
    fi

    echo "  Downloading: ${slug}.epub (Gutenberg #${gutenberg_id})"
    curl -sL --retry 3 \
        "https://www.gutenberg.org/ebooks/${gutenberg_id}.epub.noimages" \
        -o "$dest"

    if [ $? -eq 0 ] && [ -s "$dest" ]; then
        echo "  OK: ${slug}.epub"
    else
        rm -f "$dest"
        echo "  FAIL: ${slug}.epub"
    fi
}

echo "Downloading EPUBs to: $BOOKS_DIR"
echo ""

download_epub "don_quixote"               996
download_epub "the_odyssey"               1727
download_epub "hamlet"                    1524
download_epub "romeo_and_juliet"          1513
download_epub "macbeth"                   1533
download_epub "gullivers_travels"         829
download_epub "robinson_crusoe"           521
download_epub "oliver_twist"              730
download_epub "great_expectations"        1400
download_epub "david_copperfield"         766
download_epub "sense_and_sensibility"     161
download_epub "emma"                      158
download_epub "northanger_abbey"          121
download_epub "anna_karenina"             1399
download_epub "brothers_karamazov"        28054
download_epub "middlemarch"               145
download_epub "tess_of_the_durbervilles"  110
download_epub "far_from_the_madding_crowd" 107
download_epub "les_miserables"            135
download_epub "hunchback_of_notre_dame"   2610
download_epub "twenty_thousand_leagues"   164
download_epub "around_the_world_in_80_days" 103
download_epub "journey_to_center_of_earth" 18857
download_epub "time_machine"              35
download_epub "war_of_the_worlds"         36
download_epub "invisible_man"             5230
download_epub "scarlet_letter"            33
download_epub "red_badge_of_courage"      73
download_epub "call_of_the_wild"          215
download_epub "white_fang"                910
download_epub "kidnapped"                 421
download_epub "jungle_book"               236
download_epub "importance_of_being_earnest" 844
download_epub "three_musketeers"          1257
download_epub "pinocchio"                 500
download_epub "ethan_frome"               4517
download_epub "portrait_of_a_lady"        2833
download_epub "turn_of_the_screw"         209
download_epub "the_awakening"             160
download_epub "candide"                   19942
download_epub "death_of_ivan_ilyich"      600
download_epub "notes_from_underground"    4986
download_epub "heart_of_darkness"         219
download_epub "secret_garden"             113
download_epub "phantom_of_the_opera"      175
download_epub "kim"                       2226
download_epub "anne_of_green_gables"      45
download_epub "connecticut_yankee"        86
download_epub "prince_and_the_pauper"     1837
download_epub "twenty_years_after"        1259

echo ""
echo "Done."
