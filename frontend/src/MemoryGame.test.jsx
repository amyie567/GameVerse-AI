import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import MemoryGame from "./MemoryGame";

describe("MemoryGame Component", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          json: () => Promise.resolve({ message: "Points saved" }),
        }),
      ),
    );
  });

  it("should display the game title", () => {
    render(<MemoryGame />);

    expect(
      screen.getByRole("heading", { name: "Memory Match" }),
    ).toBeInTheDocument();
  });

  it("should display 16 memory cards", () => {
    render(<MemoryGame />);

    const memoryGrid = document.querySelector(".memory-grid");
    const cards = memoryGrid.querySelectorAll(".memory-card");

    expect(cards).toHaveLength(16);
  });

  it("should display zero initial moves", () => {
    render(<MemoryGame />);

    const stats = document.querySelector(".memory-stats");
    const movesStat = stats.querySelector(".memory-stat");

    expect(movesStat).toHaveTextContent("0");
    expect(movesStat).toHaveTextContent("Moves");
  });

  it("should display the restart button", () => {
    render(<MemoryGame />);

    const restartButton = document.querySelector(".memory-restart");

    expect(restartButton).toBeInTheDocument();
    expect(restartButton).toHaveTextContent("RESTART GAME");
  });
  it("should reset moves when restart is clicked", () => {
    render(<MemoryGame />);

    const memoryGrid = document.querySelector(".memory-grid");
    const firstCard = memoryGrid.querySelector(".memory-card");

    fireEvent.click(firstCard);

    const restartButton = document.querySelector(".memory-restart");

    fireEvent.click(restartButton);

    const stats = document.querySelector(".memory-stats");
    const movesStat = stats.querySelector(".memory-stat");

    expect(movesStat).toHaveTextContent("0");
  });
});
