document.addEventListener("DOMContentLoaded", function () {
    const token = window.location.pathname.split("/").pop();
    if (!token) return;

    const escapeHtml = (value) => {
        if (value === null || value === undefined || value === false) return "";
        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/\"/g, "&quot;")
            .replace(/'/g, "&#39;");
    };

    const formatValue = (value) => {
        if (value === null || value === undefined) return "—";
        if (value === false) return "Không";
        if (value === true) return "Có";
        if (Array.isArray(value)) return value[1] || value[0] || "—";
        if (typeof value === "object") {
            if (value.display_name) return value.display_name;
            if (value.name) return value.name;
            return "—";
        }
        const text = String(value).trim();
        return text || "—";
    };

    const formatFieldLabel = (fieldName) => {
        if (!fieldName) return "Thông tin";
        return fieldName
            .replace(/_id$/g, "")
            .replace(/_/g, " ")
            .replace(/\b\w/g, (char) => char.toUpperCase());
    };

    const getRenderableFields = (row, fields) => {
        const baseFields = (fields || []).filter(Boolean);
        const extraFields = Object.keys(row || {})
            .filter((key) => !baseFields.includes(key) && key !== "id" && !key.startsWith("__"))
            .sort();
        return [...baseFields, ...extraFields];
    };

    const setSummary = (screenName, viewType, recordCount) => {
        const titleEl = document.getElementById("screen_title");
        const titleMainEl = document.getElementById("screen_title_main");
        const subtitleEl = document.getElementById("screen_subtitle");
        const summaryEl = document.getElementById("screen_summary");

        if (titleEl) titleEl.innerText = screenName;
        if (titleMainEl) titleMainEl.innerText = screenName;
        if (subtitleEl) subtitleEl.innerText = `Đang hiển thị ${recordCount} bản ghi theo kiểu ${viewType === "list" ? "danh sách" : "thẻ"}.`;
        if (summaryEl) {
            summaryEl.innerHTML = `
                <span class="screen-chip screen-chip-soft"><i class="fa-solid fa-layer-group"></i> ${viewType === "list" ? "Danh sách" : "Kanban"}</span>
                <span class="screen-chip screen-chip-soft"><i class="fa-solid fa-database"></i> ${recordCount} bản ghi</span>
            `;
        }
    };

    fetch(`/api/display/data/${token}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jsonrpc: "2.0", params: {} })
    })
    .then(response => {
        if (!response.ok) throw new Error("Không thể kết nối mạng với máy chủ Odoo.");
        return response.json();
    })
    .then(res => {
        const container = document.getElementById("sb_root");
        if (!container) return;

        const result = res.result;

        if (!result) {
            container.innerHTML = `<div class="screen-empty"><i class="fa-solid fa-triangle-exclamation fs-3 mb-2 d-block"></i><strong>Mã Token không hợp lệ</strong><div class="mt-2">Cấu hình màn hình có thể đã bị tắt hoặc đường dẫn chưa đúng.</div></div>`;
            return;
        }

        if (result.error) {
            const errorMsg = typeof result.error === "object" ? JSON.stringify(result.error) : result.error;
            container.innerHTML = `<div class="screen-empty text-danger"><i class="fa-solid fa-circle-exclamation fs-3 mb-2 d-block"></i><strong>Không thể tải dữ liệu</strong><div class="mt-2">${escapeHtml(errorMsg)}</div></div>`;
            return;
        }

        const viewType = result.view_type || "list";
        const records = result.data || [];
        const fields = result.fields_list || [];

        setSummary(result.screen_name || "Screen Builder", viewType, records.length);
        container.innerHTML = "";

        if (records.length === 0) {
            container.innerHTML = `<div class="screen-empty"><i class="fa-regular fa-folder-open fs-3 mb-2 d-block"></i><strong>Chưa có bản ghi nào</strong><div class="mt-2">Mô hình hiện tại chưa có dữ liệu để hiển thị trên màn hình này.</div></div>`;
            return;
        }

        if (viewType === "list") {
            let html = `<div class="screen-table table-responsive"><table class="table table-hover align-middle mb-0"><thead><tr>`;
            const visibleFields = getRenderableFields(records[0] || {}, fields);
            visibleFields.forEach(f => {
                html += `<th class="py-3 px-4">${escapeHtml(formatFieldLabel(f))}</th>`;
            });
            html += `</tr></thead><tbody>`;

            records.forEach(row => {
                html += `<tr>`;
                const rowFields = getRenderableFields(row, fields);
                rowFields.forEach(f => {
                    const displayVal = formatValue(row[f]);
                    html += `<td class="py-3 px-4 text-secondary">${escapeHtml(displayVal)}</td>`;
                });
                html += `</tr>`;
            });
            html += `</tbody></table></div>`;
            container.innerHTML = html;
        } else if (viewType === "form") {
            let html = `<div class="row g-4">`;
            records.forEach(row => {
                const title = row.display_name || row.name || `Bản ghi #${row.id}`;
                const rowFields = getRenderableFields(row, fields);
                let bodyHtml = "";

                rowFields.forEach(f => {
                    if (f === "id" || f === "name" || f === "display_name") return;
                    const label = formatFieldLabel(f);
                    const value = formatValue(row[f]);
                    bodyHtml += `
                        <div class="col-12 col-md-6 col-xl-4">
                            <div class="border rounded-4 p-3 bg-light h-100 shadow-sm">
                                <div class="small text-uppercase text-muted mb-2">${escapeHtml(label)}</div>
                                <div class="fw-semibold text-dark">${escapeHtml(value)}</div>
                            </div>
                        </div>`;
                });

                html += `
                    <div class="col-12">
                        <div class="screen-card card h-100 border-0 shadow-sm">
                            <div class="card-body p-4">
                                <div class="d-flex flex-wrap align-items-center justify-content-between gap-2 mb-4">
                                    <div class="fw-bold" style="color:#714B67; font-size:1.08rem;">
                                        <i class="fa-solid fa-file-lines me-2 text-warning"></i>${escapeHtml(title)}
                                    </div>
                                    <span class="badge bg-light text-dark border">${row.id ? `ID #${row.id}` : "Chi tiết"}</span>
                                </div>
                                <div class="row g-3">${bodyHtml || '<div class="col-12"><div class="text-muted">Không có thông tin chi tiết</div></div>'}</div>
                            </div>
                        </div>
                    </div>`;
            });
            html += `</div>`;
            container.innerHTML = html;
        } else {
            let html = `<div class="row g-3">`;
            records.forEach(row => {
                let mainTitle = row.display_name || row.name || `Bản ghi #${row.id}`;
                let bodyFieldsHtml = "";

                fields.forEach(f => {
                    if (f !== "name" && f !== "display_name" && row[f] !== false && row[f] !== null) {
                        const label = f.replace(/_id/g, "").replace(/_/g, " ");
                        const value = formatValue(row[f]);
                        bodyFieldsHtml += `
                            <div class="mb-2" style="font-size:0.9rem; color:#4b5563;">
                                <span class="text-muted text-capitalize">${escapeHtml(label)}:</span>
                                <span class="fw-semibold text-dark">${escapeHtml(value)}</span>
                            </div>`;
                    }
                });

                html += `
                    <div class="col-12 col-sm-6 col-md-4 col-lg-3">
                        <div class="screen-card card h-100 bg-white">
                            <div class="card-body p-3 d-flex flex-column justify-content-between">
                                <div>
                                    <div class="fw-bold text-truncate mb-2" style="color:#714B67; font-size:1.05rem;">
                                        <i class="fa-solid fa-cube me-2 text-warning small"></i>${escapeHtml(mainTitle)}
                                    </div>
                                    <div class="border-top border-light pt-2 mt-2">
                                        ${bodyFieldsHtml || '<div class="text-muted small">Không có thông tin chi tiết</div>'}
                                    </div>
                                </div>
                                <div class="d-flex justify-content-between align-items-center mt-3 pt-2 border-top border-light" style="font-size:0.8rem;">
                                    <span class="text-muted">ID: #${row.id}</span>
                                    <span class="badge bg-success-subtle text-success px-2 py-1 rounded">Sẵn sàng</span>
                                </div>
                            </div>
                        </div>
                    </div>`;
            });
            html += `</div>`;
            container.innerHTML = html;
        }
    })
    .catch(err => {
        console.error("Lỗi thực thi JS:", err);
        const container = document.getElementById("sb_root");
        if (container) {
            container.innerHTML = `<div class="screen-empty text-danger"><i class="fa-solid fa-circle-exclamation fs-3 mb-2 d-block"></i><strong>Không thể kết nối</strong><div class="mt-2">${escapeHtml(err.message)}</div></div>`;
        }
    });
});