.PHONY: copy-data build clean dev install

copy-data:
	@echo "Copying data files..."
	@mkdir -p public/data/ari public/data/teiten public/data/zensu public/data/trend
	@cp ../data/ari/merged_ari.csv public/data/ari/
	@cp ../data/teiten/merged_teiten.csv public/data/teiten/
	@cp ../data/zensu/merged_zensu.csv public/data/zensu/
	@cp ../data/trend/merged_trend.csv public/data/trend/
	@echo "Data files copied successfully!"

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
