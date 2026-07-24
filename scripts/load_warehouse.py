from air_quality.warehouse_loader import load_warehouse


def main() -> None:
    processed_rows = load_warehouse()

    print(
        f"Warehouse loaded successfully: "
        f"{processed_rows} rows processed"
    )


if __name__ == "__main__":
    main()
