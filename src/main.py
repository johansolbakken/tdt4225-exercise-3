#!/usr/bin/env python3

"""
file: main.py
written by: Johan Solbakken, Morten Tobias Rinde Sunde
date: 10.10.2023

    Main file for the project.
    
"""

from app import App
import argparse

def main():
    parser = argparse.ArgumentParser(description="Nihao")
    parser.add_argument("--dataset", default="dataset/dataset", type=str, help="dataset folder")
    parser.add_argument("--nuke", action="store_true", help="nuke database")
    args = parser.parse_args()

    app = App()
    app.set_dataset(args.dataset)
    app.set_nuke(args.nuke)
    app.run()

if __name__ == "__main__":
    main()