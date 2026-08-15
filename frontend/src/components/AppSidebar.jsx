import React from 'react';
import {
  LayoutDashboard,
  Layers,
  FileSpreadsheet,
  ShieldAlert,
  BarChart3,
  Award,
  Cpu,
  Search,
  Activity,
  History,
  Settings,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

export default function AppSidebar({ activeTab, onSelectTab, collapsed, onToggleCollapse, openReviewCount = 0 }) {
  const navItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'analyzer', label: 'Product Analyzer', icon: Layers },
    { id: 'catalog', label: 'Catalog Engine', icon: FileSpreadsheet },
    {
      id: 'review',
      label: 'Review Center',
      icon: ShieldAlert,
      badge: openReviewCount > 0 ? openReviewCount : null,
      badgeColor: 'bg-rose-500 text-white'
    },
    { id: 'quality', label: 'Data Quality', icon: BarChart3 },
    { id: 'evaluation', label: 'Evaluation & Benchmarks', icon: Award },
    { id: 'governance', label: 'AI Governance', icon: Cpu },
    { id: 'search', label: 'Global Search', icon: Search },
  ];

  const adminItems = [
    { id: 'health', label: 'System Health', icon: Activity },
    { id: 'audit', label: 'Audit Log', icon: History },
  ];

  return (
    <aside
      className={`app-sidebar-container ${collapsed ? 'collapsed' : ''}`}
      style={{
        width: collapsed ? '72px' : '260px',
        backgroundColor: '#1E293B',
        borderRight: '1px solid #334155',
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        position: 'sticky',
        top: 0,
        transition: 'width 0.2s ease',
        flexShrink: 0,
        zIndex: 40
      }}
    >
      {/* Brand Header */}
      <div style={{
        height: '64px',
        borderBottom: '1px solid #334155',
        display: 'flex',
        alignItems: 'center',
        justifyContent: collapsed ? 'center' : 'space-between',
        padding: collapsed ? '0' : '0 16px'
      }}>
        {!collapsed && (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{
                background: '#2563EB',
                color: '#FFFFFF',
                fontSize: '11px',
                fontWeight: '900',
                padding: '2px 6px',
                borderRadius: '4px',
                fontFamily: 'monospace'
              }}>IQ</span>
              <span style={{ fontSize: '15px', fontWeight: '800', color: '#F8FAFC', letterSpacing: '-0.02em' }}>
                ProductIQ AI
              </span>
            </div>
            <div style={{ fontSize: '11px', color: '#94A3B8', marginTop: '2px' }}>
              Industrial Intelligence
            </div>
          </div>
        )}
        <button
          onClick={onToggleCollapse}
          title={collapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          style={{
            background: 'transparent',
            border: 'none',
            color: '#94A3B8',
            cursor: 'pointer',
            padding: '6px',
            borderRadius: '4px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
        >
          {collapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
        </button>
      </div>

      {/* Main Navigation */}
      <div style={{ flex: 1, padding: '16px 8px', overflowY: 'auto' }}>
        <div style={{
          fontSize: '10px',
          fontWeight: '700',
          color: '#64748B',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          padding: collapsed ? '0 0 8px 0' : '0 12px 8px 12px',
          textAlign: collapsed ? 'center' : 'left'
        }}>
          {collapsed ? '•' : 'Workspaces'}
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                title={collapsed ? item.label : undefined}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  width: '100%',
                  padding: collapsed ? '10px 0' : '10px 12px',
                  justifyContent: collapsed ? 'center' : 'flex-start',
                  borderRadius: '6px',
                  background: isActive ? '#2563EB' : 'transparent',
                  color: isActive ? '#FFFFFF' : '#94A3B8',
                  border: 'none',
                  fontSize: '13px',
                  fontWeight: isActive ? '600' : '500',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'background 0.15s, color 0.15s'
                }}
              >
                <Icon size={18} style={{ shrink: 0, opacity: isActive ? 1 : 0.8 }} />
                {!collapsed && (
                  <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {item.label}
                  </span>
                )}
                {!collapsed && item.badge !== null && item.badge !== undefined && (
                  <span style={{
                    background: '#EF4444',
                    color: '#FFFFFF',
                    borderRadius: '10px',
                    fontSize: '10px',
                    fontWeight: '800',
                    padding: '1px 6px'
                  }}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Administration Section */}
        <div style={{
          fontSize: '10px',
          fontWeight: '700',
          color: '#64748B',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          padding: collapsed ? '16px 0 8px 0' : '16px 12px 8px 12px',
          textAlign: collapsed ? 'center' : 'left'
        }}>
          {collapsed ? '•' : 'Operations'}
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {adminItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                title={collapsed ? item.label : undefined}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  width: '100%',
                  padding: collapsed ? '10px 0' : '10px 12px',
                  justifyContent: collapsed ? 'center' : 'flex-start',
                  borderRadius: '6px',
                  background: isActive ? '#2563EB' : 'transparent',
                  color: isActive ? '#FFFFFF' : '#94A3B8',
                  border: 'none',
                  fontSize: '13px',
                  fontWeight: isActive ? '600' : '500',
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: 'background 0.15s, color 0.15s'
                }}
              >
                <Icon size={18} style={{ shrink: 0, opacity: isActive ? 1 : 0.8 }} />
                {!collapsed && (
                  <span style={{ flex: 1, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {item.label}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      {!collapsed && (
        <div style={{
          padding: '12px 16px',
          borderTop: '1px solid #334155',
          fontSize: '11px',
          color: '#64748B'
        }}>
          <div style={{ fontWeight: '600', color: '#94A3B8' }}>v2.5.0 Enterprise</div>
          <div>Local Zero-Cost Runtime</div>
        </div>
      )}
    </aside>
  );
}
