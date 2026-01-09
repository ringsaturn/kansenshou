/**
 * Load and decompress CSV data from a zip file
 * @param {string} zipUrl - URL to the zip file
 * @returns {Promise<string>} The CSV content as text
 */
export async function loadCSVFromZip(zipUrl) {
  try {
    // Fetch the zip file
    const response = await fetch(zipUrl);
    if (!response.ok) {
      throw new Error(`Failed to fetch ${zipUrl}: ${response.statusText}`);
    }

    // Get the zip file as an ArrayBuffer
    const zipData = await response.arrayBuffer();
    
    // Parse the zip file
    const csvText = await extractCSVFromZip(zipData);
    
    return csvText;
  } catch (error) {
    console.error('Error loading CSV from zip:', error);
    throw error;
  }
}

/**
 * Extract CSV content from a zip ArrayBuffer
 * Uses a simple zip parser to avoid external dependencies
 * @param {ArrayBuffer} zipData - The zip file data
 * @returns {Promise<string>} The CSV content
 */
async function extractCSVFromZip(zipData) {
  const view = new DataView(zipData);
  let offset = 0;
  
  // Find the first file entry in the zip
  // ZIP file structure: Local file header starts with signature 0x04034b50
  while (offset < zipData.byteLength - 30) {
    const signature = view.getUint32(offset, true);
    
    if (signature === 0x04034b50) { // Local file header signature
      // Parse local file header
      const compressMethod = view.getUint16(offset + 8, true);
      const compressedSize = view.getUint32(offset + 18, true);
      const uncompressedSize = view.getUint32(offset + 22, true);
      const fileNameLength = view.getUint16(offset + 26, true);
      const extraFieldLength = view.getUint16(offset + 28, true);
      
      // Skip to file data
      const fileDataOffset = offset + 30 + fileNameLength + extraFieldLength;
      const compressedData = new Uint8Array(zipData, fileDataOffset, compressedSize);
      
      // Decompress based on method
      if (compressMethod === 0) {
        // Stored (no compression)
        const decoder = new TextDecoder('utf-8');
        return decoder.decode(compressedData);
      } else if (compressMethod === 8) {
        // Deflate compression
        const decompressedData = await decompressDeflate(compressedData);
        const decoder = new TextDecoder('utf-8');
        return decoder.decode(decompressedData);
      } else {
        throw new Error(`Unsupported compression method: ${compressMethod}`);
      }
    }
    
    offset++;
  }
  
  throw new Error('No valid file found in zip archive');
}

/**
 * Decompress deflate-compressed data using DecompressionStream API
 * @param {Uint8Array} compressedData - The compressed data
 * @returns {Promise<Uint8Array>} The decompressed data
 */
async function decompressDeflate(compressedData) {
  // Check if DecompressionStream is available
  if (typeof DecompressionStream === 'undefined') {
    throw new Error('DecompressionStream API is not available in this browser');
  }
  
  // Create a readable stream from the compressed data
  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(compressedData);
      controller.close();
    }
  });
  
  // Pipe through decompression stream
  const decompressedStream = stream.pipeThrough(
    new DecompressionStream('deflate-raw')
  );
  
  // Read all chunks
  const reader = decompressedStream.getReader();
  const chunks = [];
  
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    chunks.push(value);
  }
  
  // Combine chunks
  const totalLength = chunks.reduce((sum, chunk) => sum + chunk.length, 0);
  const result = new Uint8Array(totalLength);
  let offset = 0;
  
  for (const chunk of chunks) {
    result.set(chunk, offset);
    offset += chunk.length;
  }
  
  return result;
}
