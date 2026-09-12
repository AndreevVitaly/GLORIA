(() => {
  const input = document.querySelector('#id_photo');
  let previewUrl;
  input?.addEventListener('change', () => {
    const file = input.files[0];
    if (!file) return;
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    const preview = document.querySelector('#avatar-preview');
    previewUrl = URL.createObjectURL(file);
    preview.src = previewUrl;
    preview.hidden = false;
    const placeholder = document.querySelector('#avatar-placeholder');
    if (placeholder) placeholder.hidden = true;
  });
  document.querySelectorAll('.delete-connection').forEach(form => {
    form.addEventListener('submit', event => {
      if (!window.confirm('Удалить эту запись из окружения?')) event.preventDefault();
    });
  });
  document.querySelectorAll('.delete-recipient').forEach(form => {
    form.addEventListener('submit', event => {
      if (!window.confirm('Удалить адресата и все его памятные даты?')) event.preventDefault();
    });
  });

  const dateForms = document.querySelector('#date-forms');
  const totalForms = document.querySelector('#id_dates-TOTAL_FORMS');
  const dateTemplate = document.querySelector('#empty-date-form');
  const bindRemoveDate = container => {
    container.querySelector('.remove-date')?.addEventListener('click', () => {
      const deleteInput = container.querySelector('input[name$="-DELETE"]');
      if (deleteInput) deleteInput.checked = true;
      container.classList.add('marked-delete');
    });
  };
  dateForms?.querySelectorAll('.date-form').forEach(bindRemoveDate);
  document.querySelector('#add-date')?.addEventListener('click', () => {
    const index = Number(totalForms.value);
    const wrapper = document.createElement('div');
    wrapper.innerHTML = dateTemplate.innerHTML.replaceAll('__prefix__', String(index)).trim();
    const form = wrapper.firstElementChild;
    dateForms.appendChild(form);
    totalForms.value = String(index + 1);
    bindRemoveDate(form);
    form.querySelector('input:not([type="hidden"])')?.focus();
  });
})();
