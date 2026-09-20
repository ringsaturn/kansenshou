/**
 * Parse CSV text to array of objects
 * @param {string} csvText - CSV content as string
 * @returns {Array<Object>} Array of objects where keys are column headers
 */
export function parseCSV(csvText) {
  const lines = csvText.split("\n");
  const headers = parseHeader(lines);
  if (!headers) return [];
  const data = [];
  parseLines(lines, headers, 1, lines.length, data);
  return data;
}

/**
 * Same as parseCSV, but yields to the event loop every `chunkLines` lines so
 * the UI stays responsive while parsing large files (the trend dataset is
 * >150k rows and takes seconds to parse).
 * @param {string} csvText
 * @param {number} chunkLines
 * @returns {Promise<Array<Object>>}
 */
export async function parseCSVAsync(csvText, chunkLines = 5000) {
  const lines = csvText.split("\n");
  const headers = parseHeader(lines);
  if (!headers) return [];
  const data = [];
  for (let i = 1; i < lines.length; i += chunkLines) {
    parseLines(lines, headers, i, Math.min(i + chunkLines, lines.length), data);
    await yieldToEventLoop();
  }
  return data;
}

function yieldToEventLoop() {
  if (typeof scheduler !== "undefined" && typeof scheduler.yield === "function") {
    return scheduler.yield();
  }
  return new Promise((resolve) => setTimeout(resolve, 0));
}

function parseHeader(lines) {
  if (lines.length === 0) return null;
  const headerLine = lines[0].trim();
  if (!headerLine) return null;
  return headerLine.split(",").map((h) => h.trim());
}

function parseLines(lines, headers, from, to, out) {
  const n = headers.length;
  for (let i = from; i < to; i++) {
    let line = lines[i];
    if (line.endsWith("\r")) line = line.slice(0, -1);
    if (!line.trim()) continue;

    // Fast path: no quotes means a plain split is correct
    const values = line.includes('"') ? parseCSVLine(line) : line.split(",");
    if (values.length !== n) {
      console.warn(
        `Line ${i + 1} has ${values.length} values but expected ${n}`
      );
      continue;
    }

    const row = {};
    for (let j = 0; j < n; j++) {
      const raw = values[j];
      // Convert numeric strings to numbers (empty and "-" stay as strings)
      const num = raw === "" || raw === "-" ? NaN : +raw;
      row[headers[j]] = Number.isNaN(num) ? raw.trim() : num;
    }
    out.push(row);
  }
}

/**
 * Parse a single CSV line handling quoted fields
 * @param {string} line - A single CSV line
 * @returns {Array<string>} Array of field values
 */
function parseCSVLine(line) {
  const values = [];
  let current = "";
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];

    if (char === '"') {
      if (inQuotes && line[i + 1] === '"') {
        // Escaped quote
        current += '"';
        i++;
      } else {
        // Toggle quote state
        inQuotes = !inQuotes;
      }
    } else if (char === "," && !inQuotes) {
      // Field separator
      values.push(current);
      current = "";
    } else {
      current += char;
    }
  }

  // Add the last field
  values.push(current);

  return values;
}

/**
 * Export data to CSV format
 * @param {Array<Object>} data - Array of objects to export
 * @param {string} filename - Name of the file to download
 */
export function exportToCSV(data, filename = "export.csv") {
  if (data.length === 0) return;

  const headers = Object.keys(data[0]);
  const csvContent = [
    headers.join(","),
    ...data.map((row) =>
      headers
        .map((header) => {
          let value = row[header];
          if (value === null || value === undefined) value = "";
          // Escape quotes and wrap in quotes if contains comma or quote
          if (
            typeof value === "string" &&
            (value.includes(",") || value.includes('"'))
          ) {
            value = '"' + value.replace(/"/g, '""') + '"';
          }
          return value;
        })
        .join(",")
    ),
  ].join("\n");

  // Create download link
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  const url = URL.createObjectURL(blob);

  link.setAttribute("href", url);
  link.setAttribute("download", filename);
  link.style.visibility = "hidden";

  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
