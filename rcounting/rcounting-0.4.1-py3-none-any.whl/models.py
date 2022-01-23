import logging
from collections import defaultdict, deque

from praw.exceptions import ClientException
from prawcore.exceptions import ServerError

from rcounting import utils

printer = logging.getLogger(__name__)


class RedditPost:
    """A superclass to treat reddit comments and submissions under the same umbrella."""

    def __init__(self, post):
        self.id = post.id
        self.created_utc = post.created_utc
        self.author = str(post.author)
        self.body = post.body if hasattr(post, "body") else post.selftext
        self.submission_id = post.submission_id if hasattr(post, "submission_id") else post.name
        if hasattr(post, "post_type"):
            self.post_type = post.post_type
        else:
            self.post_type = "comment" if hasattr(post, "body") else "submission"

    def find_missing_content(self, search):
        try:
            post = next(search(ids=[self.id], metadata="true", limit=0))
        except StopIteration:
            return self.body, self.author
        author = post.author
        body = post.body if hasattr(post, "body") else post.selftext
        return body, author

    def to_dict(self):
        return {
            "username": self.author,
            "timestamp": self.created_utc,
            "comment_id": self.id,
            "submission_id": self.submission_id[3:],
            "body": self.body,
        }


class Submission(RedditPost):
    """Submissions have titles on top of all the things posts and submissions have in common"""

    def __init__(self, s):
        super().__init__(s)
        self.title = s.title

    def to_dict(self):
        return {
            "username": self.author,
            "timestamp": self.created_utc,
            "submission_id": self.submission_id[3:],
            "body": self.body,
            "title": self.title,
        }

    def __repr__(self):
        return f"offline_submission(id={self.id})"


class Comment(RedditPost):
    """
    A reddit comment class with two parts:

    The data about this comment is stored in the RedditPost object.
    Information about the tree of comments is stored in the tree member."""

    def __init__(self, comment, tree=None):
        RedditPost.__init__(self, comment)
        self.submission_id = (
            comment.submission_id if hasattr(comment, "submission_id") else comment.link_id
        )
        self.parent_id = comment.parent_id
        self.is_root = self.parent_id == self.submission_id
        self.tree = tree

    def __repr__(self):
        return f"offline_comment(id={self.id})"

    def refresh(self):
        pass

    def walk_up_tree(self, limit=None):
        return self.tree.walk_up_tree(self, limit)

    def parent(self):
        return self.tree.parent(self)

    @property
    def replies(self):
        return self.tree.find_children(self)

    @property
    def get_missing_replies(self):
        return self.tree.get_missing_replies

    @property
    def depth(self):
        return self.tree.find_depth(self)


class Tree:
    """
    A class for dealing with tree structures.

    The tree is represented as a dict, where y = tree[x] means y is the parent of x.

    Only the node ids are stored in this structure,the rest of the information
    about each node is stored in an auxiliary nodes dict
    """

    def __init__(self, nodes, tree):
        self.tree = tree
        self.nodes = nodes
        self.depths = {}

    @property
    def reversed_tree(self):
        return edges_to_tree([(parent, child) for child, parent in self.tree.items()])

    def parent(self, node):
        parent_id = self.tree[extract_id(node)]
        return self.node(parent_id)

    def find_children(self, node):
        return [self.node(x) for x in self.reversed_tree[extract_id(node)]]

    def walk_up_tree(self, node, limit=None):
        """Navigate the tree from node to root"""
        if isinstance(node, str):
            try:
                node = self.node(node)
            except KeyError:
                return None
        if node.id not in self.tree and node.id not in self.nodes:
            return None
        nodes = [node]
        counter = 1
        while node.id in self.tree and not getattr(node, "is_root", False):
            if limit is not None and counter >= limit:
                break
            node = self.parent(node)
            nodes.append(node)
            counter += 1
        return nodes

    def walk_down_tree(self, node, limit=None):
        """
        Navigate the tree from node to leaf, taking the earliest child each
        time there's a choice
        """
        if isinstance(node, str):
            node = self.node(node)
        if node.id not in self.nodes and node.id not in self.reversed_tree:
            return [node]
        result = [node]
        while node.id in self.reversed_tree:
            node = self.find_children(node)[0]
            result.append(node)
        return result

    def __len__(self):
        return len(self.tree.keys())

    def node(self, node_id):
        return self.nodes[node_id]

    def delete_edge(self, child, parent):
        child_id = extract_id(child)
        parent_id = extract_id(parent)
        if self.tree[child_id] == parent_id:
            del self.tree[child_id]

    def delete_node(self, node):
        node_id = extract_id(node)
        del self.nodes[node_id]
        if node_id in self.tree:
            del self.tree[node_id]

    def delete_subtree(self, node):
        """Delete the entire subtree rooted at the `node`"""
        queue = deque([node])
        while queue:
            node = queue.popleft()
            queue.extend(self.find_children(node))
            self.delete_node(node)

    def find_depth(self, node):
        """
        Find the depth of a node.

        The root nodes have depth 0. Otherwise, each node is one deeper than its parent.
        """
        node_id = extract_id(node)
        if node_id in self.root_ids:
            return 0
        if node_id in self.depths:
            return self.depths[node_id]
        depth = 1 + self.find_depth(self.parent(node_id))
        self.depths[node_id] = depth
        return depth

    @property
    def deepest_node(self):
        max_depth = 0
        result = None
        for leaf in self.leaves:
            depth = self.find_depth(leaf)
            if depth > max_depth:
                max_depth = depth
                result = leaf
        return result

    @property
    def leaves(self):
        leaf_ids = set(self.nodes.keys()) - set(self.tree.values())
        return [self.node(leaf_id) for leaf_id in leaf_ids]

    @property
    def roots(self):
        return [self.node(root_id) for root_id in self.root_ids]

    @property
    def root_ids(self):
        root_ids = (set(self.nodes.keys()) | set(self.tree.values())) - set(self.tree.keys())
        root_ids = [[x] if x in self.nodes else self.reversed_tree[x] for x in root_ids]
        return [root_id for ids in root_ids for root_id in ids]

    def add_nodes(self, new_nodes, new_tree):
        self.tree.update(new_tree)
        self.nodes.update(new_nodes)


class CommentTree(Tree):
    """
    A class representing the comment tree

    In addition to all the things the superclass can do, this one can use
    a reddit instance to get information about missing comments. That means
    that many of the methods for finding parents & children have to be overridden.
    """

    def __init__(self, comments=None, reddit=None, get_missing_replies=True):
        if comments is None:
            comments = []
        tree = {x.id: x.parent_id[3:] for x in comments if not is_root(x)}
        comments = {x.id: x for x in comments}
        super().__init__(comments, tree)
        self.reddit = reddit
        self.get_missing_replies = get_missing_replies
        # logger levels are 10, 20, 30, where 10 is most verbose
        self.refresh_counter = [0, 5, 2][3 - int(printer.getEffectiveLevel() // 10)]
        self._parent_counter, self._child_counter = 0, 0
        self.comment = self.node

    def node(self, node_id):
        if node_id not in self.tree and self.reddit is not None:
            self.add_missing_parents(node_id)
        return Comment(super().node(node_id), self)

    def add_comments(self, comments):
        new_comments = {x.id: x for x in comments}
        new_tree = {x.id: x.parent_id[3:] for x in comments if not is_root(x)}
        super().add_nodes(new_comments, new_tree)

    @property
    def comments(self):
        return self.nodes.values()

    def parent(self, node):
        node_id = extract_id(node)
        parent_id = self.tree[node_id]
        return self.node(parent_id)

    def add_missing_parents(self, comment_id):
        comments = []
        praw_comment = self.reddit.comment(comment_id)
        if praw_comment.is_root:
            self.add_comments([praw_comment])
            return
        try:
            praw_comment.refresh()
            if self._parent_counter == 0:
                printer.info("Fetching ancestors of comment %s", normalise(praw_comment.body))
                self._parent_counter = self.refresh_counter
            else:
                self._parent_counter -= 1
        except (ClientException, ServerError) as e:
            printer.warning("Unable to refresh %s", comment_id)
            print(e)
        for i in range(9):
            comments.append(praw_comment)
            if praw_comment.is_root:
                break
            praw_comment = praw_comment.parent()
        self.add_comments(comments)

    def fill_gaps(self):
        for node in self.roots:
            if not node.is_root:
                node.walk_up_tree()
        for leaf in self.leaves:
            if self.is_broken(leaf):
                self.delete_node(leaf)

    def find_children(self, node):
        node_id = extract_id(node)
        children = [self.comment(x) for x in self.reversed_tree[node_id]]
        if not children and self.get_missing_replies:
            children = self.add_missing_replies(node_id)
        by_date = sorted(children, key=lambda x: x.created_utc)
        return sorted(by_date, key=lambda x: x.body in utils.deleted_phrases)

    def add_missing_replies(self, comment):
        comment_id = extract_id(comment)
        praw_comment = self.reddit.comment(comment_id)
        if comment_id not in self.nodes:
            self.add_comments([comment])

        praw_comment.refresh()
        replies = praw_comment.replies
        replies.replace_more(limit=None)
        replies = replies.list()
        if replies:
            self.add_comments(replies)
            return [self.comment(x.id) for x in replies]
        return []

    def is_broken(self, comment):
        if comment.is_root:
            return False
        parent = comment.parent()
        replies = self.add_missing_replies(parent)
        if comment.id not in [x.id for x in replies]:
            return True
        return False

    def prune(self, side_thread, comment=None):
        """
        Use a side thread object to remove invalid comments and their descendants
        from the comment tree.
        """
        if comment is None:
            nodes = self.roots
        else:
            nodes = self.find_children(comment)
        queue = deque([(node, side_thread.get_history(node)) for node in nodes])
        while queue:
            node, history = queue.popleft()
            is_valid, new_history = side_thread.is_valid_count(node, history)
            if is_valid:
                queue.extend([(x, new_history) for x in self.find_children(node)])
            else:
                self.delete_subtree(node)


class SubmissionTree(Tree):
    """
    A tree that tracks submissions.

    It currently can only keep track of whether or not a submission is archived.
    """

    def __init__(self, submissions, submission_tree, reddit=None):
        self.reddit = reddit
        super().__init__(submissions, submission_tree)

    def is_archived(self, submission):
        return extract_id(submission) not in self.nodes

    def node(self, node_id):
        try:
            return super().node(node_id)
        except KeyError:
            if self.reddit is not None:
                return self.reddit.submission(node_id)
            raise


def edges_to_tree(edges):
    """
    Popupate a tree dictionary from a list of edges
    """
    tree = defaultdict(list)
    for source, dest in edges:
        tree[source].append(dest)
    return tree


def comment_to_dict(comment):
    try:
        return comment.to_dict()
    except AttributeError:
        return Comment(comment).to_dict()


def is_root(comment):
    try:
        return comment.is_root
    except AttributeError:
        parent_id = getattr(comment, "parent_id", False)
        if not parent_id:
            return False
        submission_id = (
            comment.submission_id if hasattr(comment, "submission_id") else comment.link_id
        )
        return parent_id == submission_id


def normalise(body):
    return body.split("\n")[0]


def extract_id(node):
    if hasattr(node, "id"):
        return node.id
    return node
