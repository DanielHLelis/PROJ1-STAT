#!/bin/bash

root_path=$(dirname "$0")
root_path=$(cd "$root_path" && pwd)

cd simulator-rust
cargo build --release
cd ..

mkdir -p datasets/demos

cd datasets/demos
rm ./*.json

# Run Trials Here
../../simulator-rust/target/release/simulator-rs 100000 100 0.01 20 50 0 
../../simulator-rust/target/release/simulator-rs 100000 100 0.01 20 20 0 
../../simulator-rust/target/release/simulator-rs 100000 100 0.005 20 20 0
../../simulator-rust/target/release/simulator-rs 100000 100 0.005 20 20 0.0001
../../simulator-rust/target/release/simulator-rs 100000 100 0.005 20 50 0.0001
../../simulator-rust/target/release/simulator-rs 100000 100 0.005 20 20 0.001

mv ./results/* .
rmdir results
