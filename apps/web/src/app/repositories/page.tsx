"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  FolderGit2,
  GitBranch,
  Plus,
  RefreshCw,
  ShieldCheck,
  Terminal,
} from "lucide-react";
import { api, Repository } from "@/lib/api";

export default function RepositoriesPage() {
  const [repos, setRepos] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [isAdding, setIsAdding] = useState(false);
  const [newRepoName, setNewRepoName] = useState("");
  const [newDefaultBranch, setNewDefaultBranch] = useState("main");

  const loadRepos = async () => {
    setLoading(true);
    try {
      const data = await api.getRepositories();
      setRepos(data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRepos();
  }, []);

  const handleCreateRepo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRepoName.trim()) return;
    try {
      await api.createRepository({
        full_name: newRepoName.trim(),
        default_branch: newDefaultBranch.trim() || "main",
      });
      setNewRepoName("");
      setIsAdding(false);
      loadRepos();
    } catch (err: any) {
      alert("Error adding repository: " + err.message);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-zinc-800">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Connected Repositories</h1>
          <p className="text-sm text-zinc-400 mt-1">
            Repositories monitored for Pull Request security reviews and vulnerability scans.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setIsAdding(!isAdding)}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Repository</span>
          </button>
        </div>
      </div>

      {/* Add Repository Modal/Form */}
      {isAdding && (
        <form onSubmit={handleCreateRepo} className="p-5 rounded-xl border border-zinc-700 bg-zinc-900/80 space-y-4">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider font-mono">
            Register GitHub Repository
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-mono text-zinc-400 mb-1">
                Repository Full Name (org/repo)
              </label>
              <input
                type="text"
                placeholder="e.g. acme-corp/payment-service"
                value={newRepoName}
                onChange={(e) => setNewRepoName(e.target.value)}
                required
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-xs text-zinc-200 font-mono focus:outline-none focus:border-amber-500"
              />
            </div>
            <div>
              <label className="block text-xs font-mono text-zinc-400 mb-1">
                Default Branch
              </label>
              <input
                type="text"
                placeholder="main"
                value={newDefaultBranch}
                onChange={(e) => setNewDefaultBranch(e.target.value)}
                className="w-full bg-zinc-950 border border-zinc-800 rounded-lg px-3 py-2 text-xs text-zinc-200 font-mono focus:outline-none focus:border-amber-500"
              />
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setIsAdding(false)}
              className="px-3 py-1.5 rounded-lg border border-zinc-800 text-zinc-400 text-xs hover:bg-zinc-800"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-xs"
            >
              Register
            </button>
          </div>
        </form>
      )}

      {/* Repositories List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {repos.map((repo) => (
          <div
            key={repo.id}
            className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/40 hover:border-zinc-700 transition-colors space-y-4"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center text-amber-400">
                  <FolderGit2 className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-base">{repo.full_name}</h3>
                  <div className="flex items-center gap-2 text-xs font-mono text-zinc-400">
                    <GitBranch className="w-3 h-3" />
                    <span>{repo.default_branch}</span>
                  </div>
                </div>
              </div>

              <span className="px-2 py-0.5 rounded text-[11px] font-mono font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                ACTIVE
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs font-mono pt-3 border-t border-zinc-800/80 text-zinc-400">
              <div>
                <span>Scan on PR: </span>
                <strong className="text-zinc-200">{repo.scan_on_pr ? "Enabled" : "Disabled"}</strong>
              </div>
              <div>
                <span>Review Threshold: </span>
                <strong className="text-amber-400">{repo.min_severity_for_review}</strong>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <Link
                href={`/dashboard`}
                className="text-xs font-semibold text-amber-400 hover:text-amber-300 font-mono"
              >
                View Scan Activity &rarr;
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
