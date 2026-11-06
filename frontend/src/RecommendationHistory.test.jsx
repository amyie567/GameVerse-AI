import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import RecommendationHistory from "./RecommendationHistory";

describe("RecommendationHistory Component", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ history: [] }),
        }),
      ),
    );
  });

  it("should display the recommendation history heading", () => {
    render(<RecommendationHistory />);

    expect(
      screen.getByRole("heading", {
        name: "Recommendation History",
      }),
    ).toBeInTheDocument();
  });

  it("should display loading message initially", () => {
    render(<RecommendationHistory />);

    expect(
      screen.getByText("Loading recommendation history..."),
    ).toBeInTheDocument();
  });

  it("should display empty history message when no records exist", async () => {
    render(<RecommendationHistory />);

    expect(
      await screen.findByText(
        "No recommendation history yet. Try the AI recommender first!",
      ),
    ).toBeInTheDocument();
  });
});
