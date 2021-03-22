for fn in story/*/*.txt; do
    if [[ $fn == *"None"* ]]; then
        continue
    fi
    mv "$fn" "${fn//.mp3/}"
done