"use client";

import { useActionState } from 'react';
import { authenticate } from '@/app/lib/actions';
import { Lock } from 'lucide-react';

export default function LoginForm() {
    const [errorMessage, formAction, isPending] = useActionState(authenticate, undefined);

    return (
        <form action={formAction} className="flex flex-col gap-4 w-full max-w-sm">
            <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Username</label>
                <input
                    name="username"
                    type="text"
                    defaultValue="admin"
                    className="w-full px-4 py-3 rounded-lg bg-[#111] border border-[#333] text-white focus:border-[var(--primary)] focus:outline-none transition-all"
                />
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-400 mb-1">Password</label>
                <input
                    name="password"
                    type="password"
                    defaultValue="admin"
                    className="w-full px-4 py-3 rounded-lg bg-[#111] border border-[#333] text-white focus:border-[var(--primary)] focus:outline-none transition-all"
                />
            </div>

            {errorMessage && (
                <div className="text-red-400 text-sm">
                    {errorMessage}
                </div>
            )}

            <button
                type="submit"
                aria-disabled={isPending}
                className="w-full bg-[var(--primary)] hover:bg-[var(--secondary)] text-white font-bold py-3 rounded-lg transition-colors flex justify-center items-center gap-2 mt-2"
            >
                {isPending ? 'Logging in...' : (
                    <>
                        <Lock className="w-4 h-4" /> Login
                    </>
                )}
            </button>
        </form>
    );
}
