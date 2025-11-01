import React, { useState } from 'react';
import { BookOpen, ExternalLink, Info, Sparkles } from 'lucide-react';

/**
 * EntityHighlight Component
 * 
 * Renders text with interactive highlights for detected cultural entities.
 * Shows tooltips with Wikipedia summaries on hover/click.
 */
export const EntityHighlight = ({ text, entities }) => {
    const [activeTooltip, setActiveTooltip] = useState(null);

    if (!entities || entities.length === 0) {
        return <p className="text-gray-700 leading-relaxed">{text}</p>;
    }

    // Sort entities by start position
    const sortedEntities = [...entities].sort((a, b) => a.start - b.start);

    // Build segments of text with highlights
    const segments = [];
    let currentPos = 0;

    sortedEntities.forEach((entity, index) => {
        // Add text before entity
        if (currentPos < entity.start) {
            segments.push({
                type: 'text',
                content: text.substring(currentPos, entity.start),
                key: `text-${currentPos}`
            });
        }

        // Add highlighted entity
        segments.push({
            type: 'entity',
            content: text.substring(entity.start, entity.end),
            entity: entity,
            key: `entity-${index}`
        });

        currentPos = entity.end;
    });

    // Add remaining text
    if (currentPos < text.length) {
        segments.push({
            type: 'text',
            content: text.substring(currentPos),
            key: `text-${currentPos}`
        });
    }

    // Get color based on entity type and significance
    const getEntityColor = (entity) => {
        const significance = entity.cultural_significance || 'general';

        const colorMap = {
            'mythological': 'bg-cyan-100 border-cyan-300 text-cyan-800',
            'historical': 'bg-amber-100 border-amber-300 text-amber-800',
            'literary': 'bg-teal-100 border-teal-300 text-teal-800',
            'philosophical': 'bg-sky-100 border-sky-300 text-sky-800',
            'religious': 'bg-rose-100 border-rose-300 text-rose-800',
            'artistic': 'bg-pink-100 border-pink-300 text-pink-800',
            'geographical': 'bg-green-100 border-green-300 text-green-800',
            'biographical': 'bg-emerald-100 border-emerald-300 text-emerald-800',
            'general': 'bg-gray-100 border-gray-300 text-gray-800'
        };

        return colorMap[significance] || colorMap['general'];
    };

    // Get icon for significance
    const getSignificanceIcon = (significance) => {
        return <Sparkles className="w-3 h-3 inline-block mr-1" />;
    };

    return (
        <div className="relative">
            <p className="text-gray-700 leading-relaxed">
                {segments.map((segment) => {
                    if (segment.type === 'text') {
                        return <span key={segment.key}>{segment.content}</span>;
                    }

                    const entity = segment.entity;
                    const isActive = activeTooltip === segment.key;
                    const colorClass = getEntityColor(entity);

                    return (
                        <span
                            key={segment.key}
                            className="relative inline-block group"
                        >
                            <span
                                className={`
                  ${colorClass}
                  border-b-2 cursor-help px-1 rounded
                  transition-all duration-200
                  hover:shadow-md
                  ${isActive ? 'shadow-lg' : ''}
                `}
                                onMouseEnter={() => setActiveTooltip(segment.key)}
                                onMouseLeave={() => setActiveTooltip(null)}
                                onClick={() => setActiveTooltip(isActive ? null : segment.key)}
                            >
                                {segment.content}
                            </span>

                            {/* Tooltip */}
                            {isActive && entity.summary && (
                                <div className="absolute z-50 bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-80">
                                    <div className="bg-white rounded-lg shadow-2xl border-2 border-gray-200 p-4">
                                        {/* Header */}
                                        <div className="flex items-start justify-between mb-2">
                                            <h4 className="font-semibold text-gray-900 flex items-center">
                                                {getSignificanceIcon(entity.cultural_significance)}
                                                {entity.text}
                                            </h4>
                                            <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                                                {entity.type}
                                            </span>
                                        </div>

                                        {/* Significance badge */}
                                        {entity.cultural_significance && entity.cultural_significance !== 'general' && (
                                            <div className="mb-2">
                                                <span className={`text-xs px-2 py-1 rounded ${getEntityColor(entity)}`}>
                                                    {entity.cultural_significance}
                                                </span>
                                            </div>
                                        )}

                                        {/* Summary */}
                                        <p className="text-sm text-gray-700 mb-3 leading-relaxed">
                                            {entity.summary}
                                        </p>

                                        {/* Footer */}
                                        <div className="flex items-center justify-between text-xs text-gray-500">
                                            <span className="flex items-center">
                                                <BookOpen className="w-3 h-3 mr-1" />
                                                {entity.source || 'Wikipedia'}
                                            </span>

                                            {entity.url && (
                                                <a
                                                    href={entity.url}
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="flex items-center"
                                                    style={{color: '#0A5569'}}
                                                    onClick={(e) => e.stopPropagation()}
                                                >
                                                    Learn More <ExternalLink className="w-3 h-3 ml-1" />
                                                </a>
                                            )}
                                        </div>

                                        {/* Tooltip arrow */}
                                        <div className="absolute top-full left-1/2 transform -translate-x-1/2 -mt-1">
                                            <div className="w-3 h-3 bg-white border-r-2 border-b-2 border-gray-200 transform rotate-45"></div>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </span>
                    );
                })}
            </p>
        </div>
    );
};

/**
 * EntityLegend Component
 * 
 * Shows a legend explaining entity highlight colors
 */
export const EntityLegend = () => {
    const categories = [
        { name: 'Mythological', color: 'bg-cyan-100 border-cyan-300', icon: '🔮' },
        { name: 'Historical', color: 'bg-amber-100 border-amber-300', icon: '📜' },
        { name: 'Literary', color: 'bg-teal-100 border-teal-300', icon: '📚' },
        { name: 'Philosophical', color: 'bg-sky-100 border-sky-300', icon: '💭' },
        { name: 'Religious', color: 'bg-rose-100 border-rose-300', icon: '🕊️' },
        { name: 'Geographical', color: 'bg-green-100 border-green-300', icon: '🌍' },
    ];

    return (
        <div className="bg-gray-50 rounded-lg p-4 mb-4">
            <div className="flex items-center mb-2">
                <Info className="w-4 h-4 text-gray-600 mr-2" />
                <span className="text-sm font-medium text-gray-700">Entity Highlights Legend</span>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {categories.map((cat) => (
                    <div key={cat.name} className="flex items-center text-xs">
                        <span className="mr-1">{cat.icon}</span>
                        <span className={`${cat.color} px-2 py-1 rounded border`}>
                            {cat.name}
                        </span>
                    </div>
                ))}
            </div>
            <p className="text-xs text-gray-500 mt-2">
                💡 Hover over highlighted text to see cultural context
            </p>
        </div>
    );
};

/**
 * EntitySummary Component
 * 
 * Shows summary statistics of detected entities
 */
export const EntitySummary = ({ entities }) => {
    if (!entities || entities.length === 0) {
        return null;
    }

    // Count by significance
    const counts = entities.reduce((acc, entity) => {
        const sig = entity.cultural_significance || 'general';
        acc[sig] = (acc[sig] || 0) + 1;
        return acc;
    }, {});

    const enrichedCount = entities.filter(e => e.summary).length;

    return (
        <div className="rounded-lg p-4 mb-4 border" style={{backgroundColor: '#e6f7f9', borderColor: '#b3dfe6'}}>
            <div className="flex items-center justify-between mb-2">
                <h3 className="font-semibold flex items-center" style={{color: '#0A5569'}}>
                    <Sparkles className="w-5 h-5 mr-2" />
                    Cultural Entities Detected
                </h3>
                <span className="text-white px-3 py-1 rounded-full text-sm font-bold" style={{backgroundColor: '#0A5569'}}>
                    {entities.length}
                </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-sm">
                <div className="bg-white rounded p-2">
                    <div className="text-gray-600 text-xs">Total Found</div>
                    <div className="font-bold" style={{color: '#0A5569'}}>{entities.length}</div>
                </div>
                <div className="bg-white rounded p-2">
                    <div className="text-gray-600 text-xs">Enriched</div>
                    <div className="font-bold text-green-600">{enrichedCount}</div>
                </div>
                {Object.entries(counts).slice(0, 2).map(([sig, count]) => (
                    <div key={sig} className="bg-white rounded p-2">
                        <div className="text-gray-600 text-xs capitalize">{sig}</div>
                        <div className="font-bold text-gray-800">{count}</div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default EntityHighlight;
