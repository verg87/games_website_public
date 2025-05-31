import { createElementFromString } from "./boardSaving.js";
import { getPiece } from "./boardSaving.js";
import { getKeyByValue } from "./boardSaving.js";

export class ChessLogic {
  constructor() {
    this.letters = ["a", "b", "c", "d", "e", "f", "g", "h"];
    this.state = {
      winner: undefined,
      pieceMoved: undefined,
    };
    this.eventListeners = {
      "black-queen": [],
      "black-horse": [],
      "black-rook": [],
      "black-bishop": [],
      "white-queen": [],
      "white-horse": [],
      "white-rook": [],
      "white-bishop": [],
    };
  }

  enPassant() {
    const direction = this.state.pieceMoved[0] === "B" ? 1 : -1;

    const enemyPawnId =
      this.state.processedCell[0] + (Number(this.state.processedCell[1]) + direction);

    const enemyPawn = document.getElementById(enemyPawnId);
    const child = enemyPawn.querySelector('img');

    enemyPawn.removeChild(child);
  }

  wrapper(pieceName, choices, body, eventName) {
    const self = this;

    if (eventName === "click") {
      return function curriedEventListerner(e) {
        self.promote(pieceName, choices, body);
      };
    } else if (eventName === "mouseover") {
      return function curriedEventListerner(e) {
        self.checkForCheck(e, body);
      };
    }
  }

  checkForCheck(event, body) {
    const pieceClass = event.currentTarget.classList[1];
    const dashIndex = pieceClass.indexOf("-");
    const piece =
      pieceClass[0].toUpperCase() + pieceClass[dashIndex + 1].toUpperCase();

    delete body.eventType;
    body.pieceMoved = piece;

    this.sendMove(body);
  }

  promote(chosenPiece, choices, body) {
    for (let option in choices) {
      const pieceOption = choices[option][1];
      const haveOtherPieceInside = pieceOption.querySelector("img");

      pieceOption.classList.remove(pieceOption.classList[1]);

      if (haveOtherPieceInside) {
        haveOtherPieceInside.style.display = "";
      }

      // * Remove event listeners if piece is chosen
      pieceOption.removeEventListener("click", this.eventListeners[option][0]);
      pieceOption.removeEventListener(
        "mouseover",
        this.eventListeners[option][1]
      );
    }

    const pieceName = choices[chosenPiece][0];
    const pieceString = getPiece(pieceName);
    const pieceElement = createElementFromString(pieceString);

    const row = pieceName[0] === "B" ? "1" : "8";

    const promotionCell = document.getElementById(
      choices[chosenPiece][1].id[0] + row
    );

    promotionCell.appendChild(pieceElement);

    body.pawnPromotedTo = choices[chosenPiece][0];
    body.pieceMoved = choices[chosenPiece][0];
    body.eventType = "click";

    if (this.state.isCheck) {
      let color;
      let piece = promotionCell.querySelector("img").dataset.id;

      if (piece[0] === "B") {
        color = "W";
      } else if (piece[0] === "W") {
        color = "B";
      }

      const king = document.getElementById(color + "K");

      this.addCheckEffect(king);
    }

    if (this.state.isCheckmate) {
      this.handleCheckmate();
    }

    this.sendMove(body);
  }

  promoteHandler(body) {
    for (let letter of this.letters) {
      const firstRow = document.getElementById(letter + "1");
      const lastRow = document.getElementById(letter + "8");

      if (firstRow.querySelector("img")) {
        this.isPawnOnTheLastRow(firstRow, body, 1);
      }
      if (lastRow.querySelector("img")) {
        this.isPawnOnTheLastRow(lastRow, body, -1);
      }
    }
  }

  isPawnOnTheLastRow(firstCell, body, direction) {
    const side = direction === 1 ? "black-" : "white-";

    const queen = side + "queen";
    const horse = side + "horse";
    const rook = side + "rook";
    const bishop = side + "bishop";

    const piece = firstCell.querySelector("img");
    const pawn = side.charAt(0).toUpperCase() + "P";

    if (piece.dataset.id === pawn) {
      firstCell.removeChild(piece);
      firstCell.classList.add(queen);

      let secondOption = document.getElementById(
        firstCell.id[0] + (Number(firstCell.id[1]) + direction)
      );
      let thirdOption = document.getElementById(
        firstCell.id[0] + (Number(firstCell.id[1]) + direction * 2)
      );
      let forthOption = document.getElementById(
        firstCell.id[0] + (Number(firstCell.id[1]) + direction * 3)
      );

      const choices = {
        [queen]: direction === 1 ? ["BQ", firstCell] : ["WQ", firstCell],
        [horse]: direction === 1 ? ["BH", secondOption] : ["WH", secondOption],
        [rook]: direction === 1 ? ["BR", thirdOption] : ["WR", thirdOption],
        [bishop]: direction === 1 ? ["BB", forthOption] : ["WB", forthOption],
      };

      for (let option of [secondOption, thirdOption, forthOption]) {
        const haveOtherPieceInside = option.querySelector("img");
        const appropriateClass = getKeyByValue(choices, option);

        if (haveOtherPieceInside) {
          haveOtherPieceInside.style.display = "none";
        }

        option.classList.add(appropriateClass);
      }

      for (const pieceOption of Object.keys(choices)) {
        this.eventListeners[pieceOption][0] = this.wrapper(
          pieceOption,
          choices,
          body,
          "click"
        );
        this.eventListeners[pieceOption][1] = this.wrapper(
          pieceOption,
          choices,
          body,
          "mouseover"
        );

        choices[pieceOption][1].addEventListener(
          "click",
          this.eventListeners[pieceOption][0]
        );
        choices[pieceOption][1].addEventListener(
          "mouseover",
          this.eventListeners[pieceOption][1]
        );
      }
    }
  }

  addCheckEffect(kingIdentifier) {
    const parentKingCell = kingIdentifier.parentNode;
    parentKingCell.classList.add("check");
  }

  checkForRookThreat(enemyKing) {
    let kingId, enemyRookId;

    if (enemyKing.id[0] === "W") {
      kingId = "BK";
      enemyRookId = "WR";
    } else if (enemyKing.id[0] === "B") {
      kingId = "WK";
      enemyRookId = "BR";
    }

    const enemyKingElement = document.getElementById(kingId);

    let kingColumnIndex = this.letters.indexOf(
      enemyKingElement.parentNode.id[0]
    );
    let kingRowIndex = Number(enemyKingElement.parentNode.id[1]);

    for (let direction of [1, -1]) {
      let currentRow = kingRowIndex;
      let currentCol = kingColumnIndex;

      // Check vertically
      while (currentRow > 0 && currentRow <= 8) {
        let cellId = this.letters[kingColumnIndex] + String(currentRow);

        if (cellId !== enemyKingElement.parentNode.id) {
          let cellElement = document.getElementById(cellId);
          let pieceElement = cellElement.querySelector("img");

          if (pieceElement) {
            let pieceId = pieceElement.dataset.id;
            if (pieceId === enemyRookId) {
              this.addCheckEffect(enemyKingElement);
              break;
            } else {
              break;
            }
          }
        }
        currentRow += direction;
      }

      // Reset currentRow and check horizontally
      currentRow = kingRowIndex;
      while (currentCol >= 0 && currentCol < 8) {
        let cellId = this.letters[currentCol] + kingRowIndex;

        if (cellId !== enemyKingElement.parentNode.id) {
          let cellElement = document.getElementById(cellId);
          let pieceElement = cellElement.querySelector("img");

          if (pieceElement) {
            let pieceId = pieceElement.dataset.id;
            if (pieceId === enemyRookId) {
              this.addCheckEffect(enemyKingElement);
              break;
            } else {
              break;
            }
          }
        }
        currentCol += direction;
      }
    }
  }

  handleCheckmate() {
    const chessBoard = document.getElementById("board");
    const header = document.createElement("h1");

    chessBoard.style.pointerEvents = "none";

    this.state.winner =
      this.state.winner[0].toUpperCase() + this.state.winner.slice(1);
    const text = document.createTextNode(
      `${this.state.winner} won by checkmate, you can play again by pressing reset button`
    );
    header.appendChild(text);

    document.body.insertBefore(header, document.body.firstChild);
  }

  castle(row, rookColumn, kingColumnAfterCastle, rookColumnAfterCastle) {
    const rookCell = document.getElementById(rookColumn + row);
    const rook = rookCell.querySelector("img");

    const kingCell = document.getElementById("e" + row);
    const king = kingCell.querySelector("img");

    rookCell.removeChild(rook);
    kingCell.removeChild(king);

    document.getElementById(kingColumnAfterCastle + row).appendChild(king);
    document.getElementById(rookColumnAfterCastle + row).appendChild(rook);

    this.checkForRookThreat(king);
  }

  handleCastle(originCell, destinationCell) {
    let row = "8";
    if (this.state.pieceMoved[0] == "W") {
      row = "1";
    }

    if (
      this.letters.indexOf(originCell[0]) <
      this.letters.indexOf(destinationCell[0])
    ) {
      this.castle(row, "h", "g", "f");
    } else {
      this.castle(row, "a", "c", "d");
    }
  }

  isKingCastles(oldCell, newCell) {
    const oldRow = Number(oldCell[1]);
    const newRow = Number(newCell[1]);
    const oldCol = this.letters.indexOf(oldCell[0]);
    const newCol = this.letters.indexOf(newCell[0]);

    const allowedCells = ["a", "g", "c", "h"];
    const oldCellInTheDOM = document.getElementById(oldCell);

    if (!allowedCells.includes(newCell[0])) {
      return false;
    }

    if (!oldCellInTheDOM.querySelector("img")) {
      return false;
    }

    // If king in check then it should be able to castle
    // if (oldCellInTheDOM.classList.contains('check')) {
    //   return false;
    // }

    if (oldCellInTheDOM.querySelector("img").dataset.id[1] != "K") {
      return false;
    }

    if (newCol > oldCol) {
      const gCell = document.getElementById("g" + oldRow.toString());
      const fCell = document.getElementById("f" + oldRow.toString());

      if (gCell.querySelector("img") || fCell.querySelector("img")) {
        return false;
      }
    } else if (newCol < oldCol) {
      const bCell = document.getElementById("b" + oldRow.toString());
      const cCell = document.getElementById("c" + oldRow.toString());
      const dCell = document.getElementById("d" + oldRow.toString());

      if (
        bCell.querySelector("img") ||
        cCell.querySelector("img") ||
        dCell.querySelector("img")
      ) {
        return false;
      }
    }

    if ((oldRow === 8 || oldRow === 1) && (newRow === 8 || newRow === 1)) {
      // Check if the king moves two squares horizontally and stays on the same row
      if (Math.abs(oldCol - newCol) >= 2 && oldRow === newRow) {
        return true;
      }
    }

    return false;
  }
}
