import { handleKeyDown } from "./boardSaving.js";
import { ChessLogic } from "./chessLogic.js";

class ChessGame extends ChessLogic {
  constructor(webSocket) {
    super();
    this.cells = document.querySelectorAll(".black-cell, .white-cell");
    this.ws = webSocket;
    this.state = {
      dragged: undefined,
      startingCell: undefined,
      validMove: undefined,
      winner: undefined,
      isCheck: undefined,
      isCheckmate: undefined,
      isCastle: undefined,
      pieceMoved: undefined,
      processedCell: undefined,
      isEnPassant: undefined,
    };
    this.sendTime = null;

    // Calls initDrag
    this.initDrag();
  }

  sendMove(body) {
    if (this.ws.readyState === 1) {
      try {
        this.sendTime = performance.now();
        this.ws.send(JSON.stringify(body));
      } catch (error) {
        console.error("WebSocket send failed:", error);
      }
    } else {
      console.warn("WebSocket not open; move not sent");
    }
  }

  initDrag() {
    document.addEventListener("keydown", handleKeyDown, false);
    this.cells.forEach((cell) => {
      cell.addEventListener("dragstart", this.handleDragStart.bind(this));
      cell.addEventListener("dragover", this.handleDragOver.bind(this), false);
      cell.addEventListener("dragenter", this.handleDragEnter.bind(this));
      cell.addEventListener("dragleave", this.handleDragLeave.bind(this));
      cell.addEventListener("dragend", this.handleDragEnd.bind(this));
      cell.addEventListener("drop", this.handleDrop.bind(this));
    });
  }

  handleDragStart(event) {
    this.state.dragged = event.target;
    // console.log(event.target);
    this.state.startingCell = event.target.closest(
      ".black-cell, .white-cell"
    ).dataset.cell;
  }

  handleDragOver(event) {
    if (this.state.validMove) {
      event.preventDefault();
    }
  }

  handleDragEnter(event) {
    if (
      !event.currentTarget.classList.contains("dropzone") &&
      this.state.validMove
    ) {
      event.currentTarget.classList.add("dropzone");
    }

    const endCell = event.currentTarget.dataset.cell;
    this.state.pieceMoved = this.state.dragged.dataset.id;
    // console.log(this.state.dragged);

    this.state.isCastle = this.isKingCastles(this.state.startingCell, endCell);

    const body = {
      oldCell: this.state.startingCell,
      newCell: endCell,
      pieceMoved: this.state.pieceMoved,
    };

    try {
      this.sendMove(body);

      this.ws.addEventListener("message", (e) => {
        const data = JSON.parse(e.data)

        this.state.winner = data.winner;
        this.state.isCheckmate = data.checkmate;
        this.state.isCheck = data.check;
        this.state.validMove = data.move_valid;
        this.state.processedCell = data.processed_cell;
        this.state.isEnPassant = data.en_passant;

        const receiveTime = performance.now();
        if (this.sendTime !== null) {
          const latency = receiveTime - this.sendTime;
          console.log(
            `WebSocket move round-trip time: ${latency.toFixed(2)} ms`
          );
          this.sendTime = null; // Reset for next measurement
        }
      });
    } catch (error) {
      console.error("Validation error:", error);
      this.state.validMove = false;
    } finally {
      this.state.isValidating = false;
    }
  }

  handleDragLeave(event) {
    event.currentTarget.classList.remove("dropzone");
  }

  handleDragEnd(event) {
    this.cells.forEach((cell) => {
      cell.classList.remove("dropzone");
    });

    if (
      this.state.validMove &&
      event.currentTarget.id === this.state.processedCell
    ) {
      const cell = event.currentTarget.dataset.cell;

      let body = {
        pieceMoved: this.state.pieceMoved,
        oldCell: this.state.startingCell,
        newCell: cell,
        eventType: "dragend",
        castle: this.state.isCastle,
      };

      cell === this.state.startingCell ? (body.pieceMoved = false) : null;

      this.promoteHandler(body);

      // const data = JSON.stringlify(body);
      // this.ws.send(data);
      // * Both methods work fine but lower one is cleaner
      this.sendMove(body);
    }
  }

  handleDrop(event) {
    event.preventDefault();

    try {
      if (
        this.state.validMove &&
        event.currentTarget.id === this.state.processedCell
      ) {
        const piece = event.currentTarget.querySelector("img");
        const originCell = this.state.dragged.parentNode.dataset.cell;
        const destinationCell = event.currentTarget.dataset.cell;

        const permission = this.isKingCastles(originCell, destinationCell);

        if (piece && !permission) {
          event.currentTarget.removeChild(piece);
        }

        this.cells.forEach((cell) => {
          cell.classList.remove("check");
        });

        if (permission) {
          this.handleCastle(originCell, destinationCell);
        } else {
          event.currentTarget.appendChild(this.state.dragged);
          event.currentTarget.classList.remove("dropzone");
        }
        
        if (this.state.isEnPassant) {
          this.enPassant();
        }

        if (this.state.isCheck) {
          let color;
          let piece = event.currentTarget.querySelector("img").dataset.id;

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
      }
    } catch (error) {
      console.error(error);
      this.state.validMove = false;
    }
  }
}

const webSocket = new WebSocket(`ws://${window.location.host}/ws/chess//`);

webSocket.addEventListener("open", (e) => {
  new ChessGame(webSocket);
});
