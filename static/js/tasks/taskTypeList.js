const deleteModal = document.getElementById("deleteTaskTypeModal");
deleteModal.addEventListener("show.bs.modal", function (event) {
  const button = event.relatedTarget;
  const typeId = button.getAttribute("data-type-id");
  const typeName = button.getAttribute("data-type-name");

  const form = document.getElementById("deleteTaskTypeForm");
  const nameSpan = document.getElementById("deleteTypeName");

  form.action = `${taskTypesUrl}${typeId}/delete/`;
  nameSpan.textContent = typeName;
});

document.body.addEventListener("htmx:afterSwap", function (evt) {
  const target = evt.detail.target;
  let modalId = null;

  if (target.id === "createTaskTypeModalBody") {
    modalId = "createTaskTypeModal";
  }
  if (target.id === "updateTaskTypeModalBody") {
    modalId = "updateTaskTypeModal";
  }

  const modal = bootstrap.Modal.getInstance(document.getElementById(modalId));
  const formStillExists = target.querySelector("form") !== null;

  if (!formStillExists) {
    modal?.hide();
  }
});

function openModal(modalId) {
  const modal = new bootstrap.Modal(document.getElementById(modalId));
  modal.show();
}
