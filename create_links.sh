#!/bin/bash

source_dir="/home/hiesl/linux/shell_files/bash_files"
target_dir="/home/hiesl/.local/bin"

cd "$source_dir" || exit

for file in *; do
    if [ -f "$file" ]; then
        ln -s "$(realpath "$file")" "$target_dir/$file"
    fi
done
