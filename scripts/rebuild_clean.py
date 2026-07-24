from air_quality.clean_builder import rebuild_clean_csv


def main() -> None:
    clean_file = rebuild_clean_csv()
    print(f"Clean CSV rebuilt: {clean_file}")


if __name__ == "__main__":
    main()
