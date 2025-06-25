ckan.module('org-tree-toggle', function($, _) {
  return {
    initialize: function () {
      const module = this;

      console.log('org-tree-toggle module initialized'); // Helpful for debugging

      module.el.on('click', '.toggle-btn', function () {
        const $btn = $(this);
        const orgName = $btn.data('org');
        const $childrenContainer = $('#children_' + orgName);

        if ($childrenContainer.is(':visible')) {
          $childrenContainer.hide();
          $btn.text('+');
        } else {
          if ($childrenContainer.children().length === 0) {
            $.getJSON('/api/3/action/group_tree_section', {
              id: orgName,
              type: 'organization',
              include_parents: false,
              include_siblings: false
            }, function (data) {
              if (data.success) {
                console.log('Children for', orgName, ':', data.result.children);

                const children = data.result.children;

                const renderNode = (node) => `
                  <li id="node_${node.name}" style="list-style: none;">
                    <div class="d-flex align-items-center gap-2 node">
                      ${node.children && node.children.length > 0 
                        ? `<button class="toggle-btn" data-org="${node.name}">+</button>` 
                        : ''
                      }
                      <h3 class="organization-heading m-0">
                        <a href="/organization/${node.name}">${node.title}</a>
                      </h3>
                    </div>
                    <ul class="children ps-4" id="children_${node.name}" style="display:none;"></ul>
                  </li>
                `;

                const items = children.map(renderNode);
                $childrenContainer.html(items.join('')).show();
                $btn.text('−');
              } else {
                console.error('API call failed:', data);
              }
            });
          } else {
            $childrenContainer.show();
            $btn.text('−');
          }
        }
      });
    }
  };
});
