/**
 * Parse CSV text to array of objects
 * @param {string} csvText - CSV content as string
 * @returns {Array<Object>} Array of objects where keys are column headers
 */
export function parseCSV(csvText) {
  const lines = csvText.trim().split("\n");
  if (lines.length === 0) return [];

  // Parse header
  const headers = lines[0].split(",").map((h) => h.trim());

  // Parse data rows
  const data = [];
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i];
    if (!line.trim()) continue;

    const values = parseCSVLine(line);
    if (values.length !== headers.length) {
      console.warn(
        `Line ${i + 1} has ${values.length} values but expected ${
          headers.length
        }`
      );
      continue;
    }

    const row = {};
    headers.forEach((header, index) => {
      let value = values[index].trim();

      // Convert numeric strings to numbers
      if (value !== "" && value !== "-" && !isNaN(value)) {
        value = parseFloat(value);
      }

      row[header] = value;
    });

    data.push(row);
  }

  return data;
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
