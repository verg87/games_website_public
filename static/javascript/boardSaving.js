// Constants for board state management
const BOARD_STORAGE_KEY = "board";
const EMPTY_CELL_VALUE = "empty";


export function getKeyByValue(object, value) {
  return Object.keys(object).find(key => object[key].includes(value));
}

/**
 * Creates a DOM element from an HTML string
 * @param {string} html - The HTML string to convert to a DOM element
 * @returns {Element} The created DOM element
 * @throws {Error} If the HTML string is invalid
 */
export function createElementFromString(html) {
  if (!html || typeof html !== 'string') {
    throw new Error('Invalid HTML string provided');
  }
  
  let template = document.createElement("template");
  template.innerHTML = html.trim();
  return template.content.firstElementChild;
}

/**
 * Analyzes the state of a row and returns an object representing each cell's content
 * @param {Element} row - The row element to analyze
 * @returns {Object} An object mapping cell positions to their content (piece ID or 'empty')
 * @throws {Error} If the row element is invalid
 */
function checkRow(row) {
  if (!row || !row.children) {
    throw new Error('Invalid row element provided');
  }

  let rowState = {};
  Array.from(row.children).forEach(cell => {
    const images = cell.getElementsByTagName("img");
    rowState[cell.dataset.cell] = images.length > 0 
      ? images[0].dataset.id 
      : EMPTY_CELL_VALUE;
  });

  return rowState;
}

/**
 * Generates HTML for a chess piece based on its name
 * @param {string} name - The name/ID of the chess piece
 * @returns {string} HTML string for the piece image or empty string if piece not found
 */
export function getPiece(name) {
  if (!name || typeof name !== 'string') {
    console.error('Invalid piece name provided');
    return "";
  }

  if (pieceImages.hasOwnProperty(name)) {
    return `<img class="piece" data-id="${name}" src="${pieceImages[name]}" draggable="true">`;
  }
  
  console.error(`Error: the image: '${name}' wasn't found`);
  return "";
}

/**
 * Updates the board state in localStorage and returns the current board state
 * @returns {Object} The current board state
 */
function updateLocalStorageBoard() {
  try {
    const boardFromLocalStorage = JSON.parse(localStorage.getItem(BOARD_STORAGE_KEY));
    const boardFromGetBoard = JSON.stringify(getBoard());

    if (boardFromLocalStorage !== boardFromGetBoard) {
      localStorage.setItem(BOARD_STORAGE_KEY, boardFromGetBoard);
      return JSON.parse(boardFromGetBoard);
    }
    return boardFromLocalStorage;
  } catch (error) {
    console.error('Error updating board state:', error);
    return getBoard();
  }
}

/**
 * Gets the current state of the entire board
 * @returns {Object} An object representing the current state of the board
 * @throws {Error} If the board element is not found
 */
function getBoard() {
  const boardElement = document.getElementById("board");
  if (!boardElement) {
    throw new Error('Board element not found');
  }

  const board = {};
  Array.from(boardElement.children).forEach(row => {
    board[row.id] = checkRow(row);
  });

  return board;
}

/**
 * Sets the board state by updating the DOM with the provided board configuration
 * @param {Object} board - The board state to apply
 * @throws {Error} If the board state is invalid
 */
function setBoard(board) {
  if (!board || typeof board !== 'object') {
    throw new Error('Invalid board state provided');
  }

  const boardElement = document.getElementById("board");
  if (!boardElement) {
    throw new Error('Board element not found');
  }

  Array.from(boardElement.children).forEach(row => {
    // Remove all existing pieces from the row
    const images = row.getElementsByTagName("img");
    Array.from(images).forEach(img => img.remove());

    // Add new pieces according to the board state
    const currentRow = board[row.id];
    if (!currentRow) return;

    Array.from(row.children).forEach(cell => {
      const cellState = currentRow[cell.dataset.cell];
      if (cellState && cellState !== EMPTY_CELL_VALUE) {
        const pieceString = getPiece(cellState);
        const piece = createElementFromString(pieceString);
        cell.appendChild(piece);
      }
    });
  });
}

/**
 * Handles keyboard events for board saving functionality
 * @param {KeyboardEvent} event - The keyboard event to handle
 */
export function handleKeyDown(event) {
  if (event.key === "F5") {
    event.preventDefault();
    
    try {
      if (!localStorage.getItem(BOARD_STORAGE_KEY)) {
        const board = getBoard();
        localStorage.setItem(BOARD_STORAGE_KEY, JSON.stringify(board));
        setBoard(board);
      } else {
        const board = updateLocalStorageBoard();
        setBoard(board);
      }
    } catch (error) {
      console.error('Error handling board state:', error);
    }
  }
}