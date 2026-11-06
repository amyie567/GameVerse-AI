import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import PlayerProfile from "./PlayerProfile";
import { fireEvent } from "@testing-library/react";

const mockProfile = {
  username: "AmitGamer",
  level: 5,
  favorite_genre: "Action",
  games_played: 25,
  total_points: 600,
  mini_game_points: 100,
  achievements: [
    {
      name: "First Adventure",
      icon: "🏆",
      description: "Complete your first adventure.",
    },
    {
      name: "Speed Master",
      icon: "⚡",
      description: "Master your speed.",
    },
  ],
};

describe("PlayerProfile Component", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () => Promise.resolve(mockProfile),
        }),
      ),
    );
  });

  it("should display loading message initially", () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => new Promise(() => {})),
    );

    render(<PlayerProfile />);

    expect(screen.getByText("Loading profile...")).toBeInTheDocument();
  });

  it("should display the profile heading", async () => {
    render(<PlayerProfile />);

    expect(
      await screen.findByRole("heading", {
        name: "Your Gaming Profile",
      }),
    ).toBeInTheDocument();
  });

  it("should display the player's username", async () => {
    render(<PlayerProfile />);

    expect(await screen.findByText("AmitGamer")).toBeInTheDocument();
  });

  it("should display the player's favorite genre", async () => {
    render(<PlayerProfile />);

    expect(
      await screen.findByText("Favorite Genre: Action"),
    ).toBeInTheDocument();
  });

  it("should display player statistics", async () => {
    render(<PlayerProfile />);

    expect(await screen.findByText("25")).toBeInTheDocument();
    expect(await screen.findByText("600")).toBeInTheDocument();
    expect(await screen.findByText("100")).toBeInTheDocument();
    expect(await screen.findByText("Games Played")).toBeInTheDocument();
    expect(await screen.findByText("Total Points")).toBeInTheDocument();
    expect(await screen.findByText("Mini-Game Points")).toBeInTheDocument();
  });
  it("should allow the player to edit their username", async () => {
    render(<PlayerProfile />);

    const usernameInput = await screen.findByLabelText("Player Username");

    fireEvent.change(usernameInput, {
      target: { value: "NewGamer" },
    });

    expect(usernameInput).toHaveValue("NewGamer");
  });
  it("should save the updated username", async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockProfile),
      }),
    );

    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            message: "Profile updated successfully!",
            profile: {
              ...mockProfile,
              username: "NewGamer",
            },
          }),
      }),
    );

    render(<PlayerProfile />);

    const usernameInput = await screen.findByLabelText("Player Username");

    fireEvent.change(usernameInput, {
      target: { value: "NewGamer" },
    });

    fireEvent.click(screen.getByRole("button", { name: "SAVE PROFILE" }));

    expect(
      await screen.findByText("Profile updated successfully!"),
    ).toBeInTheDocument();

    expect(usernameInput).toHaveValue("NewGamer");
  });
  it("should update the favorite genre", async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockProfile),
      }),
    );

    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            message: "Genre updated successfully!",
            profile: {
              ...mockProfile,
              favorite_genre: "Racing",
            },
          }),
      }),
    );

    render(<PlayerProfile />);

    const genreSelect = await screen.findByLabelText("Favorite Genre");

    fireEvent.change(genreSelect, {
      target: { value: "Racing" },
    });

    expect(
      await screen.findByText("Genre updated successfully!"),
    ).toBeInTheDocument();

    expect(genreSelect).toHaveValue("Racing");
  });
  it("should display player achievements", async () => {
    render(<PlayerProfile />);

    expect(
      await screen.findByRole("heading", { name: "Achievements" }),
    ).toBeInTheDocument();

    expect(
      await screen.findByRole("heading", { name: "First Adventure" }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("heading", { name: "Speed Master" }),
    ).toBeInTheDocument();
  });
  it("should unlock a test achievement", async () => {
    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve(mockProfile),
      }),
    );

    fetch.mockImplementationOnce(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            message: "Achievement unlocked!",
            profile: {
              ...mockProfile,
              achievements: [
                ...mockProfile.achievements,
                {
                  name: "Gaming Champion",
                  icon: "🏆",
                  description: "You are a champion!",
                },
              ],
            },
          }),
      }),
    );

    render(<PlayerProfile />);

    await screen.findByRole("heading", {
      name: "Your Gaming Profile",
    });

    fireEvent.click(
      screen.getByRole("button", {
        name: /UNLOCK TEST ACHIEVEMENT/,
      }),
    );

    expect(
      await screen.findByText("Achievement unlocked!"),
    ).toBeInTheDocument();

    expect(
      await screen.findByRole("heading", {
        name: "Gaming Champion",
      }),
    ).toBeInTheDocument();
  });
  it("should display an error when the backend connection fails", async () => {
    fetch.mockRejectedValueOnce(new Error("Network error"));

    render(<PlayerProfile />);

    expect(
      await screen.findByText("Could not connect to the profile server."),
    ).toBeInTheDocument();
  });
  it("should display an error when profile loading fails", async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
    });

    render(<PlayerProfile />);

    expect(
      await screen.findByText("Could not connect to the profile server."),
    ).toBeInTheDocument();
  });
  it("should display an error when username update fails", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockProfile),
    });

    fetch.mockResolvedValueOnce({
      ok: false,
    });

    render(<PlayerProfile />);

    const usernameInput = await screen.findByLabelText("Player Username");

    fireEvent.change(usernameInput, {
      target: { value: "NewGamer" },
    });

    fireEvent.click(screen.getByRole("button", { name: "SAVE PROFILE" }));

    expect(
      await screen.findByText("Unable to update profile. Try again."),
    ).toBeInTheDocument();
  });
  it("should display an error when genre update fails", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockProfile),
    });

    fetch.mockResolvedValueOnce({
      ok: false,
    });

    render(<PlayerProfile />);

    const genreSelect = await screen.findByLabelText("Favorite Genre");

    fireEvent.change(genreSelect, {
      target: { value: "Racing" },
    });

    expect(
      await screen.findByText("Unable to update genre."),
    ).toBeInTheDocument();
  });
  it("should display an error when achievement unlocking fails", async () => {
    fetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockProfile),
    });

    fetch.mockResolvedValueOnce({
      ok: false,
    });

    render(<PlayerProfile />);

    await screen.findByRole("heading", {
      name: "Your Gaming Profile",
    });

    fireEvent.click(
      screen.getByRole("button", {
        name: /UNLOCK TEST ACHIEVEMENT/,
      }),
    );

    expect(
      await screen.findByText("Unable to unlock achievement."),
    ).toBeInTheDocument();
  });
});
