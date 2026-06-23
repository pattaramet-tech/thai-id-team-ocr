const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface Team {
  id: number;
  name: string;
  ageGroup: string;
  gender: string;
  createdAt: string;
}

export interface TeamCreate {
  name: string;
  ageGroup: string;
  gender: string;
}

export const api = {
  teams: {
    list: async (): Promise<Team[]> => {
      const res = await fetch(`${API_BASE_URL}/teams`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) throw new Error("Failed to fetch teams");
      return res.json();
    },

    create: async (team: TeamCreate): Promise<Team> => {
      const res = await fetch(`${API_BASE_URL}/teams`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(team),
      });
      if (!res.ok) throw new Error("Failed to create team");
      return res.json();
    },

    get: async (id: number): Promise<Team> => {
      const res = await fetch(`${API_BASE_URL}/teams/${id}`, {
        method: "GET",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) throw new Error("Failed to fetch team");
      return res.json();
    },

    update: async (id: number, team: Partial<TeamCreate>): Promise<Team> => {
      const res = await fetch(`${API_BASE_URL}/teams/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(team),
      });
      if (!res.ok) throw new Error("Failed to update team");
      return res.json();
    },

    delete: async (id: number): Promise<void> => {
      const res = await fetch(`${API_BASE_URL}/teams/${id}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
      });
      if (!res.ok) throw new Error("Failed to delete team");
    },
  },
};
