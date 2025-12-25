import LoginForm from '@/app/ui/login-form';

export default function LoginPage() {
    return (
        <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-black">
            <div className="w-full max-w-md bg-[#0a0a0a] border border-[#333] rounded-2xl p-8 shadow-2xl">
                <h1 className="text-2xl font-bold text-white mb-6 text-center">
                    Research<span className="text-[var(--primary)]">Obsidian</span> Access
                </h1>
                <LoginForm />
            </div>
        </div>
    );
}
