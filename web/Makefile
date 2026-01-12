.PHONY: copy-data build build-vue build-observable clean dev dev-query dev-all install

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
	@echo "Installing Observable dependencies..."
	@cd observable && bun install

dev: copy-data
	@echo "Starting Vue development server..."
	@bun run dev

dev-query:
	@echo "Starting Observable query interface..."
	@bun run dev:query

dev-all: copy-data
	@echo "Starting both Vue and Observable servers..."
	@echo "Vue: http://localhost:3000"
	@echo "Observable: http://localhost:3001"
	@(bun run dev & cd observable && observable preview)

build-vue: copy-data
	@echo "Building Vue app..."
	@bun run build:vue
	@echo "Vue build completed!"

build-observable:
	@echo "Building Observable app..."
	@bun run build:query
	@echo "Observable build completed! Output in dist/query/"

build: copy-data build-vue build-observable
	@echo "==================================="
	@echo "Build completed!"
	@echo "Vue app: dist/"
	@echo "Observable app: dist/query/"
	@echo "==================================="
	@echo "The Observable app is accessible at: /query/"
	@echo "Deploy the entire dist/ directory to your hosting service."

clean:
	@echo "Cleaning up..."
	@rm -rf dist
	@rm -rf public/data
	@rm -rf observable/dist
	@rm -rf observable/.observablehq/cache
	@echo "Cleanup completed!"

preview: build
	@echo "Starting preview server..."
	@bun run preview
