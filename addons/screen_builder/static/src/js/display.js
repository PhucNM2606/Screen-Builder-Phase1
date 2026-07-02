document.addEventListener("DOMContentLoaded", function () {
    const token = window.location.pathname.split("/").pop();
    if (!token) return;

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

        // Xử lý an toàn: Lấy phần dữ liệu thực tế nằm trong thuộc tính 'result' của gói tin JSON-RPC
        const result = res.result;
        
        if (!result) {
            container.innerHTML = `<div class="alert alert-danger">Mã Token không hợp lệ hoặc cấu hình màn hình đã bị tắt.</div>`;
            return;
        }

        if (result.error) {
            // Sửa lỗi hiển thị [object Object]: Biến đổi object thành chuỗi chữ đọc được
            const errorMsg = typeof result.error === 'object' ? JSON.stringify(result.error) : result.error;
            container.innerHTML = `<div class="alert alert-danger">Lỗi hệ thống: ${errorMsg}</div>`;
            return;
        }

        if (result.screen_name) {
            const titleEl = document.getElementById("screen_title");
            if (titleEl) titleEl.innerText = result.screen_name;
        }

        container.innerHTML = ""; // Xóa vòng xoay loading

        const viewType = result.view_type || 'list';
        const records = result.data || [];
        const fields = result.fields_list || [];

        if (records.length === 0) {
            container.innerHTML = `<div class="text-center py-5 text-muted"><i class="fa-regular fa-folder-open fs-2 mb-2 d-block"></i>Mô hình hiện chưa có bản ghi nào để hiển thị.</div>`;
            return;
        }

        if (viewType === 'list') {
            // --- DỰNG LIST VIEW (BẢNG THÔNG TIN DỘNG) ---
            let html = `<div class="table-responsive shadow-sm rounded bg-white"><table class="table table-hover align-middle mb-0"><thead><tr class="table-light">`;
            fields.forEach(f => {
                html += `<th class="py-3 px-4">${f.toUpperCase().replace('_ID', '')}</th>`;
            });
            html += `</tr></thead><tbody>`;
            
            records.forEach(row => {
                html += `<tr>`;
                fields.forEach(f => {
                    let val = row[f];
                    let displayVal = Array.isArray(val) ? val[1] : (val !== false && val !== null ? val : '-');
                    html += `<td class="py-3 px-4 text-secondary">${displayVal}</td>`;
                });
                html += `</tr>`;
            });
            html += `</tbody></table></div>`;
            container.innerHTML = html;

        } else {
            // --- DỰNG KANBAN VIEW (KHỐI THẺ RENDER CHUẨN ODOO) ---
            let html = `<div class="row g-3">`;
            records.forEach(row => {
                let mainTitle = row.display_name || row.name || `Bản ghi #${row.id}`;
                let bodyFieldsHtml = '';
                
                fields.forEach(f => {
                    if (f !== 'name' && f !== 'display_name' && row[f] !== false && row[f] !== null) {
                        let label = f.replace('_id', '');
                        let value = Array.isArray(row[f]) ? row[f][1] : row[f];
                        bodyFieldsHtml += `
                            <div class="o_card_field text-truncate mb-1" style="font-size:0.85rem; color:#4a5568;">
                                <span class="text-muted text-capitalize">${label}:</span> 
                                <span class="fw-semibold text-dark">${value}</span>
                            </div>`;
                    }
                });

                html += `
                    <div class="col-12 col-sm-6 col-md-4 col-lg-3">
                        <div class="o_kanban_record card shadow-sm h-100 bg-white">
                            <div class="card-body p-3 d-flex flex-column justify-content-between">
                                <div>
                                    <div class="fw-bold text-truncate mb-2" style="color:#714B67; font-size:1.05rem;">
                                        <i class="fa-solid fa-cube me-2 text-warning small"></i>${mainTitle}
                                    </div>
                                    <div class="border-top border-light pt-2 mt-1">
                                        ${bodyFieldsHtml}
                                    </div>
                                </div>
                                <div class="d-flex justify-content-between align-items-center mt-3 pt-2 border-top border-light" style="font-size:0.8rem;">
                                    <span class="text-muted">ID: #${row.id}</span>
                                    <span class="badge bg-success-subtle text-success px-2 py-1 rounded">Vận hành</span>
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
        document.getElementById("sb_root").innerHTML = `<div class="alert alert-danger">Lỗi kết nối API: ${err.message}</div>`;
    });
});