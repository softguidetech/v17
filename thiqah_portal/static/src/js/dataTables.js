// $(function () {
//   $.extend($.fn.dataTable.defaults, {
//     autoWidth: true,

//     dom: '<"datatable-header"fl><"datatable-scroll"t><"datatable-footer"ip>',
//     language: {
//       search:
//         '<div class="form-control-feedback form-control-feedback-end flex-fill"><div class="form-control-feedback-icon"><i class="fa fa-search opacity-50"></i></div>_INPUT_</div>',
//       searchPlaceholder: "Search...",
//       lengthMenu:
//         '<span class="body2" style="color: #798793 !important">Enties Shown:</span> _MENU_',
//       paginate: {
//         first: "First",
//         last: "Last",
//         next: "Next",
//         previous: "Previous",
//       },
//     },
//   });
//   $("#projects_details_table").DataTable({ responsive: true });
// });
// // $(function () {
// //   $.extend($.fn.dataTable.defaults, {
// //     // autoWidth: true,
// //     columnDefs: [{ orderable: false, targets: -1 }],
// //     bSort: false,
// //     dom: '<"datatable-scroll"t>',
// //   });
// //   $("#financialTableView").DataTable({ responsive: true });
// // });

// $(function () {
//   $.extend($.fn.dataTable.defaults, {
//     autoWidth: true,
//     columnDefs: [{ orderable: false, targets: -1 }],
//     bSort: false,
//     dom: '<"datatable-header"f><"datatable-scroll"tp>',
//     language: {
//       search:
//         '<div class="form-control-feedback form-control-feedback-end flex-fill"><div class="form-control-feedback-icon"><i class="fa fa-search opacity-50"></i></div>_INPUT_</div>',
//       searchPlaceholder: "Search...",
//       lengthMenu:
//         '<span class="body2" style="color: #798793 !important">Enties Shown:</span> _MENU_',
//       paginate: {
//         first: "First",
//         last: "Last",
//         next: "Next",
//         previous: "Previous",
//       },
//     },
//   });
//   $("#service_requests_table").DataTable({});
//   const serviceRequeststHeader = $("#service_requests_table")
//     .parent()
//     .siblings(".datatable-header");
//   serviceRequeststHeader.append(`
//   <div class="align-items-center d-flex header_actions">
//   <a t-attf-href="#"
//   class="_generate_excel btn btn-sm rounded-pill t-btn-outile-light-gray-secondary"> Download <svg class="ml-3"
//   xmlns="http://www.w3.org/2000/svg" width="14" height="16"
//   fill="none">
//   <path fill="#0A0A0A"
//   d="M2.66 16h8.5c1.55 0 2.328-.77 2.328-2.297V6.307c0-1.527-.778-2.298-2.327-2.298H9.093v1.193h2.046c.733 0 1.156.4 1.156 1.171v7.263c0 .77-.423 1.17-1.156 1.17H2.675c-.74 0-1.148-.4-1.148-1.17V6.373c0-.77.407-1.17 1.148-1.17h2.053V4.008H2.661C1.11 4.01.333 4.78.333 6.307v7.396C.333 15.229 1.112 16 2.66 16Zm4.247-4.876c.156 0 .281-.045.43-.193l2.505-2.423a.525.525 0 0 0 .178-.386c0-.304-.238-.519-.542-.519a.53.53 0 0 0-.4.178L7.952 8.975l-.497.526.045-1.112V.578A.597.597 0 0 0 6.907 0a.59.59 0 0 0-.586.578v7.811l.045 1.112-.504-.526-1.12-1.194a.557.557 0 0 0-.407-.178c-.31 0-.533.215-.533.52 0 .155.06.273.17.385l2.505 2.423c.156.148.282.193.43.193Z" />
//   </svg>
//   </a>
//   <div class="ml-2 dropdown">
//     <button class="btn  btn-sm dropdown-toggle rounded-pill t-btn-outile-light-gray-secondary t-text-gray" type="button" data-toggle="dropdown" aria-expanded="false">
//     Sort by
//     </button>
//     <div class="dropdown-menu dropdown-menu-right">
//     <a class="dropdown-item button-text border-bottom" href="/my/requests?sortby=date_desc">Newest</a>
//     <a class="dropdown-item button-text" href="/my/requests?sortby=date_asc">Oldest</a>
//     </div>
//   </div>
//   <div class="ml-2 dropdown">
//     <button class="btn  btn-sm dropdown-toggle rounded-pill t-btn-outile-light-gray-secondary t-text-gray" type="button" data-toggle="dropdown" aria-expanded="false">
//     Filter by
//     </button>
//     <div class="ml-2 dropdown-menu dropdown-menu-right">
//       <a class="dropdown-item button-text" href="/my/requests?filterby=all&amp;sortby=date_asc" class="dropdown-item active">
//                                         <span>All</span>
//       </a>
//       <a class="dropdown-item button-text" href="/my/requests?filterby=last_month&amp;sortby=date_asc" class="dropdown-item">
//                                         <span>Last month</span>
//       </a>
//       <a class="dropdown-item button-text" href="/my/requests?filterby=last_week&amp;sortby=date_asc" class="dropdown-item">
//                                         <span>Last week</span>
//       </a>
//       <a class="dropdown-item button-text" href="/my/requests?filterby=last_year&amp;sortby=date_asc" class="dropdown-item">
//                                         <span>Last year</span>
//       </a>
//       <a class="dropdown-item button-text" href="/my/requests?filterby=month&amp;sortby=date_asc" class="dropdown-item">
//                                         <span>This month</span>
//       </a>
//       <a class="dropdown-item button-text" href="/my/requests?filterby=quarter&amp;sortby=date_asc" class="dropdown-item">
//                                         <span>This Quarter</span>
//       </a>
//       <a class="dropdown-item button-text" href="/my/requests?filterby=today&amp;sortby=date_asc" class="dropdown-item">
//                                         <span>Today</span>
//       </a>
//       <a class="dropdown-item button-text" href="/my/requests?filterby=week&amp;sortby=date_asc" class="dropdown-item">
//                                         <span>This week</span>
//       </a>
//       <a class="dropdown-item button-text" href="/my/requests?filterby=year&amp;sortby=date_asc" class="dropdown-item">
//                                         <span>This year</span>
//       </a>
//     </div>
//   </div>
//   </div>`);
// });
