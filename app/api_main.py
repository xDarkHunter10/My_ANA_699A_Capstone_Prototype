from fastapi import FastAPI
from pydantic import BaseModel
import chess
import chess.pgn
from io import StringIO

app = FastAPI(title="Simple Chess Coach API", version="1.0")

SAMPLE_POSITIONS = {
    "Starting Position": chess.STARTING_FEN,
    "Italian Game": "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 2 3",
    "Queen's Gambit": "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq - 0 2",
    "Sicilian Defense": "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2",
}

class MovesRequest(BaseModel):
    moves: str

class FenRequest(BaseModel):
    fen: str

class OpeningRequest(BaseModel):
    rating_band: str
    color: str
    style: str
    time_control: str


def board_from_moves(moves_text: str):
    board = chess.Board()
    cleaned = moves_text.replace("\n", " ").strip()
    if not cleaned:
        return board, []
    tokens = [t for t in cleaned.split() if "." not in t and not t.startswith("{")]
    parsed = []
    for token in tokens:
        try:
            move = board.parse_san(token)
            board.push(move)
            parsed.append(token)
        except Exception:
            break
    return board, parsed


def explain_position(board: chess.Board):
    legal_moves = list(board.legal_moves)
    recommendations = []
    for move in legal_moves[:5]:
        san = board.san(move)
        reasons = []
        if board.is_capture(move):
            reasons.append("wins or contests material")
        piece = board.piece_at(move.from_square)
        if piece and piece.piece_type in [chess.KNIGHT, chess.BISHOP] and board.fullmove_number <= 10:
            reasons.append("develops a minor piece early")
        if piece and piece.piece_type == chess.PAWN and chess.square_file(move.to_square) in [3, 4]:
            reasons.append("fights for the center")
        if board.gives_check(move):
            reasons.append("creates immediate pressure on the king")
        if not reasons:
            reasons.append("is a safe, practical move for many players")
        recommendations.append({
            "move": san,
            "why": "; ".join(reasons),
            "difficulty": "Low" if len(reasons) <= 1 else "Medium"
        })
    summary = []
    if board.fullmove_number <= 10:
        summary.append("This looks like an opening position, so development and center control matter most.")
    if board.is_check():
        summary.append("The side to move is in check, so king safety is the first priority.")
    if not summary:
        summary.append("This position is better handled by choosing clear, practical moves over flashy ones.")
    return {"summary": " ".join(summary), "recommendations": recommendations}


def opening_advice(rating_band: str, color: str, style: str, time_control: str):
    openings = {
        ("Beginner", "White", "Solid"): ("London System", "Easy setup, low memorization, and a clear plan for newer players."),
        ("Beginner", "White", "Aggressive"): ("Italian Game", "Active piece play without being too theory-heavy."),
        ("Beginner", "Black", "Solid"): ("Caro-Kann Defense", "Reliable structure and fewer early tactical disasters."),
        ("Beginner", "Black", "Aggressive"): ("Scandinavian Defense", "Straightforward ideas and early queen activity to create pressure."),
        ("Intermediate", "White", "Solid"): ("Queen's Gambit", "Strong central play with plans that reward understanding more than memorization."),
        ("Intermediate", "White", "Aggressive"): ("Open Sicilian as White", "Sharp positions if you want to push for initiative."),
        ("Intermediate", "Black", "Solid"): ("Slav Defense", "Healthy structure and logical development."),
        ("Intermediate", "Black", "Aggressive"): ("Sicilian Defense", "Gives winning chances but requires more tactical alertness."),
    }
    opening, reason = openings.get((rating_band, color, style), ("Italian Game", "Simple piece development and clear plans."))
    coach = f"For a {rating_band.lower()} {color.lower()} player in {time_control.lower()}, {opening} fits because it matches a {style.lower()} style and keeps the decisions manageable."
    return {"opening": opening, "reason": reason, "coach_message": coach}


@app.get("/")
def root():
    return {"message": "Simple Chess Coach API is running"}


@app.get("/sample-positions")
def sample_positions():
    return {"positions": SAMPLE_POSITIONS}


@app.post("/analyze-fen")
def analyze_fen(payload: FenRequest):
    board = chess.Board(payload.fen)
    analysis = explain_position(board)
    return {"fen": payload.fen, **analysis}


@app.post("/analyze-moves")
def analyze_moves(payload: MovesRequest):
    board, parsed = board_from_moves(payload.moves)
    analysis = explain_position(board)
    return {
        "parsed_moves": parsed,
        "fen": board.fen(),
        **analysis
    }


@app.post("/recommend-opening")
def recommend_opening(payload: OpeningRequest):
    return opening_advice(payload.rating_band, payload.color, payload.style, payload.time_control)
