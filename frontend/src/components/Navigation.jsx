import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { BookOpen, LogOut, User } from 'lucide-react';

function Navigation({ user, onLogout }) {
    const navigate = useNavigate();
    const location = useLocation();

    return (
        <nav className="bg-white shadow-sm sticky top-0 z-40">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16">
                    <div
                        className="flex items-center gap-2 cursor-pointer"
                        onClick={() => navigate('/')}
                    >
                        <BookOpen className="w-8 h-8" style={{ color: '#0A5569' }} />
                        <span className="text-xl font-bold" style={{ color: '#0A5569' }}>
                            Cultural Context Analyzer
                        </span>
                    </div>
                    <div className="flex items-center gap-3">
                        {user ? (
                            <>
                                <div className="flex items-center gap-2 text-gray-700">
                                    <User className="w-4 h-4" />
                                    <span className="text-sm font-medium">{user.name}</span>
                                </div>
                                {location.pathname !== '/analyzer' && (
                                    <button
                                        onClick={() => navigate('/analyzer')}
                                        className="px-4 py-2 rounded-lg font-medium transition-colors"
                                        style={{ color: '#0A5569' }}
                                    >
                                        Analyzer
                                    </button>
                                )}
                                <button
                                    onClick={onLogout}
                                    className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                                    style={{ backgroundColor: '#e6f7f9', color: '#0A5569' }}
                                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#ccf2f6'}
                                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#e6f7f9'}
                                >
                                    <LogOut className="w-4 h-4" />
                                    Logout
                                </button>
                            </>
                        ) : (
                            <>
                                <button
                                    onClick={() => navigate('/login')}
                                    className="px-4 py-2 rounded-lg font-medium transition-colors"
                                    style={{ color: '#0A5569' }}
                                >
                                    Sign In
                                </button>
                                <button
                                    onClick={() => navigate('/register')}
                                    className="px-6 py-2 rounded-lg font-medium text-white transition-all hover:shadow-lg"
                                    style={{ backgroundColor: '#0A5569' }}
                                >
                                    Get Started
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
}

export default Navigation;
