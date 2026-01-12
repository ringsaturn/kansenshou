.PHONY: copy-data build clean dev install

copy-data:
	@echo "Copying and compressing data files..."
	@mkdir -p public/data/ari public/data/teiten public/data/zensu public/data/trend
	@zip -j public/data/ari/merged_ari.zip ../data/ari/merged_ari.csv
	@zip -j public/data/teiten/merged_teiten.zip ../data/teiten/merged_teiten.csv
	@zip -j public/data/zensu/merged_zensu.zip ../data/zensu/merged_zensu.csv
	@zip -j public/data/trend/merged_trend.zip ../data/trend/merged_trend.csv
	@echo "Data files compressed and copied successfully!"

install:
	@echo "Installing dependencies..."
	@bun install

dev: copy-data
	@echo "Starting development server..."
	@bun run dev

build: copy-data
	@echo "Building for production..."
	@bun run build
	@echo "Build completed! Output in dist/"

clean:
	@echo "Cleaning up..."
	@rm -rf dist
	@rm -rf public/data
	@echo "Cleanup completed!"

preview: build
	@echo "Starting preview server..."
	@bun run preview
